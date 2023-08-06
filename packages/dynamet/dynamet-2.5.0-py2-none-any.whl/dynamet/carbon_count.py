# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 09:09:16 2014

@author: pkiefer
 number of feture carbom atoms is estimated by 3 different methods: 
    (1) from natural labeled samples
"""
import emzed
import numpy as np
from emzed.core.data_types import Table
from peakmaps2feature_tables import regroup_and_cluster_features 
from helper_funs import determine_fgrouper_rttol
import objects_check as checks
import helper_funs as helper
import iso_corr
import re
MMU=emzed.MMU


    
def estimate_C_from_db(samples, db=None):
    """ estimates No of possible carbon atoms from data _base. if no data base chosen pubchem db
        filterd for CHNOPS is used
    """
    pairs=_build_fid_mass_pairs_from_samples(samples)
    delta_m=12
    if db==None:        
        db=emzed.db.load_pubchem()
    num_c=dict()
    print 'Done.'
    print
    print 'matching possible molecular formulas for detected features'
    print' This  might take severeal minutes...'
    for fid, m in pairs:
       mfs=db.filter(db.m0.inRange(m-delta_m, m+delta_m)).mf
       c_count=[count_element('C', mf) for mf in mfs if count_element('C', mf)>=1]
       num_c[fid]=(min(c_count), max(c_count))
    print 'Done.'
    return num_c


def _build_fid_mass_pairs_from_samples(samples):
    """
    """
    overall=emzed.utils.mergeTables(samples)
    overall.addColumn('_temp', overall.feature_mz_min*overall.z)
    return list(set(zip(overall.feature_id.values, overall._temp.values)))


def count_element(el, mf):
    """Alphabetic order of elements in MF: 
    """
    def num2str(v):
        if v=='':
            return 1
        else:
            return int(v) 
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    selected=[num2str(number) for element, number in fields if element==el]
    return int(sum(selected))


def estimate_num_c_nl(table, integration=False, lin_abs_error=0.03):
    """ high resolution peak: (m1-m0)*z ==1.00335 with mass accuracy of 0.5*MMU
       relative error of orbitrap 3% of max value
    """
    assert isinstance(table, Table), 'object is not a Table'
    required=['feature_id', 'num_isotopes', 'area']
    checks.table_has_colnames(required, table)
    if integration:
        n_cpus=checks._get_n_cpus(table)
        table=emzed.utils.integrate(table, 'max', n_cpus=n_cpus)
    num_c=dict()
    def num_C(m0, m1, lb_error=lin_abs_error*0.3, ub_error=lin_abs_error):
        p12 = emzed.abundance.C[12]
        c_est=int(round(m1*(1.0)/m0*p12/(1-p12)))
        c_min=int(np.floor((m1-m0*lb_error)/m0*p12/(1-p12)))
        c_max=int(np.ceil((m1+m0*ub_error)/m0*p12/(1-p12)))
        return c_est, c_min, c_max
    features=table.splitBy('feature_id')
    for f in features:
        pairs=zip(f.num_isotopes.values, f.area.values)
        a_m0=min(pairs, key=lambda v: v[0])[1]
        a_m1=[v[1] for v in pairs if v[0]==1 ]
        if len(a_m1) and a_m0:
            a_m1=a_m1[0]
            c_est, min_c, max_c=num_C(a_m0, a_m1)
        else:
            c_est, min_c, max_c=None, None, None
        key=f.feature_id.uniqueValue()
        num_c[key]= c_est, min_c, max_c
    return  num_c


def estimate_min_C_mass_traces(samples):
    """input: samples from labeling sequence with unique feature_id's 
       output: minimum number of carbon atoms 
    """
    assert isinstance(samples, list), 'function requires list of tables'
    required=['feature_id', 'mz', 'z']
    for s in samples:
        assert isinstance(s, Table), 'list elements are not Tables'
        checks.table_has_colnames(required, s)
    num_c=dict()
    overall=emzed.utils.mergeTables(samples, force_merge=True)
    features=overall.splitBy('feature_id')
    for f in features:
        num_c[f.feature_id.uniqueValue()]=(_get_min_c(f), None)
    return num_c


def _get_min_c(feature):
    f=feature
    helper.get_num_isotopes(f)
    min_c=f.num_isotopes.max()
    f.dropColumns('num_isotopes')
    return min_c


def estimate_num_c_idms(t_nl, t_idms, isol_width=3*MMU, rttol=10, p_c_source=0.99):
    required_nl=['num_isotopes']
    checks.table_has_colnames(required_nl,t_nl)
    # get monoisotopic peaks of natural labeled features
    print 'extracting monisotopic peaks from natural labeled sample...'
    ref_m0=t_nl.filter(t_nl.num_isotopes==0)
    print 'identifying monoistopic peaks in m0 mul table....'
    t_m0, t_ul=_ident_common_features(ref_m0, t_idms, isol_width=isol_width, rttol=rttol)
    rttol_pattern=determine_fgrouper_rttol([t_idms])
    potential=potential_idms_pairs(t_m0, t_ul, rttol=rttol_pattern)
    potential=get_expected_distribution(potential, p_c_source=p_c_source)
    num_c=get_best_scored(potential)
    return num_c

  
def _ident_common_features(ref_m0, t_idms, isol_width=3*emzed.MMU, rttol=10):
    """extracts all monoisotopic reference peaks of ref_m0 from t
        required: U13C are not part of the nl feature !!!! (given if ff_metabo is applied) 
    """
    rtmin=ref_m0.rt-rttol
    rtmax=ref_m0.rt+rttol
    common=t_idms.join(ref_m0, t_idms.mz.approxEqual(ref_m0.mz, isol_width)\
        & t_idms.rt.inRange(rtmin, rtmax) & ((t_idms.z==ref_m0.z) | (t_idms.z==0)))
    # now all peaks identified are with postfix '' and those of ref_column with '__0'
    # extract monoistopic peaks directly from t_idms
    #exclusion of complete feature:
    selected=common.id.values
    t_ul=t_idms.filter(~t_idms.id.isIn(selected))
    # z must be replaced since 0 is allowed
    pairs=list(set(zip(common.feature_id.values, common.z__0.values)))
    replace_z=_build_dict(pairs)
    helper.update_column_by_dict(t_idms, 'z', 'feature_id', replace_z)
    # to do not mix up feature_ids between idms and t0 in potential_idms_pairs: 
    # keep original fid values and add ref_m0 values in temp_column
    common.addColumn('fid', common.feature_id__0)
    replace=['z'] # since z might be 0  in t_idms
    postfix=common.supportedPostfixes(replace)[-1]
    for rep in replace:
        common.replaceColumn(rep, common.getColumn(rep+postfix))
    colnames=[n  for n in t_idms.getColNames()]
    colnames.append('fid')
    t_m0=common.extractColumns(*colnames)
    return t_m0, t_ul


def potential_idms_pairs(t_m0, t_ul, rttol=5, mztol=0.8*MMU):   
    """ input t_m0 monoisotopic peaks of natural labeled feature, tul, all other features
        of idms table splitted into two table by _ident_common_features
    """
    assert t_m0.peakmap.uniqueValue()==t_ul.peakmap.uniqueValue(), 'table t_m0 and tul do not'\
            'originate from same peakmap!'
    delta_c=emzed.mass.C13-emzed.mass.C12
    z_crit = ((t_m0.z==t_ul.z) | (t_ul.z==0))
    rt_crit = (t_ul.rt.inRange(t_m0.rt-rttol, t_m0.rt+rttol))
    m0mul=t_m0.join(t_ul, rt_crit &z_crit)
    m0mul.addColumn('temp',(m0mul.mz__0-m0mul.mz)*m0mul.z*1.0, format_='%.5f')
    m0mul=m0mul.filter(m0mul.temp>=(1.0033-0.5*emzed.MMU))# at least 1 carbon atom
    m0mul.addColumn('temp1',m0mul.temp.apply(lambda v: abs(v-round(v)*delta_c)), format_='%.5f')
    m0mul=m0mul.filter(m0mul.temp1<mztol)
    redundant_crit=(m0mul.feature_id==m0mul.feature_id__0)\
                    | (~m0mul.feature_id__0.isIn(m0mul.feature_id.values))
    m0mul=m0mul.filter(redundant_crit)
    # assigning overall feature_ids.
    m0mul.replaceColumn('feature_id', m0mul.fid)
    m0mul.addColumn('c_distance',((m0mul.z*m0mul.mz__0-m0mul.mz*m0mul.z)/delta_c).apply(round), 
                                    type_=int, format_='%d')
    m0mul.replaceColumn('c_distance', m0mul.c_distance.apply(int))
    m0mul.dropColumns('temp', 'temp1')
    return m0mul


def get_expected_distribution(m0ul, p_c_source=0.99):
    features=m0ul.splitBy('feature_id')
    subtables=[]
    for f in features:
        values= _group_consecutive(f.c_distance.values)
        def _fun(v, pairs=values):
            for pair in pairs:
                if v==pair[0]:
                    return pair[1]
        f.addColumn('grouped',f.c_distance.apply(_fun))
        subs=f.splitBy('grouped')
        for sub in subs:
            sub.addColumn('mi_frac', sub.area__0/sub.area__0.sum())
            expected=_expected_pattern(sub.c_distance.values, p=p_c_source)
            sub.addColumn('mi_expected', expected)
            subtables.append(sub)
            get_n_c(sub)
    return emzed.utils.mergeTables(subtables)

    
def _expected_pattern(ns, p=0.99, n_max=150):
    """ calculates the expected carbon distribution
    """
    n=max(ns)
    if n<n_max:
        dist=iso_corr.bin_dist(n,p)
        found=[dist[i] for i in ns]
        return[v/sum(found) for v  in found]
    else:
        return [x for x in np.zeros(len(ns))]
    

def get_n_c(f):
    # scoring and selection
    # calculate median area ratio a_m0/ a_ul
    if len(f):
        pairs=zip(f.c_distance.values, f.mi_frac.values, f.mi_expected.values)
        rel_delta=sum([abs(v[1]-v[2])/v[2] for v in pairs])
        max_n=[]
        for j in range(3):
            try:
                value=[v[0] for v in pairs if v[j]==max([x[j] for x in pairs])]
            except:
                print pairs[j]
            if len(value)==1:
                max_n.append(value[0])
            else:
               max_n.append(-1)
        if len(max_n):
            score=1
            if max(f.mi_expected.values)==0.0:
                score=0
        if len(pairs)>1:
            if max_n[1]==max_n[2]:
                score+=2
            else:
               score+=-1
        f.updateColumn('n_c_by_is', max_n[0])
        f.updateColumn('score_by_is', score)
        f.updateColumn('rel_delta', rel_delta)


def get_best_scored(t):
    required=['feature_id', 'n_c_by_is', 'score_by_is', 'rel_delta']
    checks.table_has_colnames(required, t)
    tuples=set(zip(t.feature_id, t.n_c_by_is, t.score_by_is, t.rel_delta))
    num_c=dict()
    for tupl in tuples:
        if num_c.has_key(tupl[0]):
            if num_c[tupl[0]][-2]<tupl[-2]:
                num_c[tupl[0]]=tupl[1:]
            elif num_c[tupl[0]][-2]==tupl[-2]:
                if num_c[tupl[0]][-1]>tupl[-1]:
                    num_c[tupl[0]]=tupl[1:]
        else:
            num_c[tupl[0]]=tupl[1:]
    return num_c

        
def _build_dict(pairs):
    if len(pairs):
        exchange=dict()
        for pair in pairs:
            if not exchange.has_key(pair[0]):
                exchange[pair[0]]=pair[1]
        return exchange

    
def _group_consecutive(values):
    assert isinstance(values,tuple)
    # if sorting in place values.sort() order 
    values=sorted(values)
    delta=[0]
    delta.extend([values[i+1]-values[i] for i in range(len(values)-1)])
    groups=[]
    m=0
    for x in delta:
        if x!=1:
            m+=1
        groups.append(m)
    return zip(values, groups)


def build_overall_table_from_dicts(d1, d2, d3, d4):
    keys=d1.keys()
    keys.extend(d2.keys())
    keys.extend(d3.keys())
    keys.extend(d4.keys())
    keys=list(set(keys))
    t=emzed.utils.toTable('feature_id', keys)
    def fun(v, d, i):
        if d.has_key(v):
            return d[v][i]
    t.addColumn('num_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,0)), format_='%d')
    t.addColumn('min_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,1)), format_='%d')
    t.addColumn('max_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,2)), format_='%d')
    if len(d2):
        t.addColumn('num_c_by_is', t.feature_id.apply(lambda v: fun(v,d2,0)), format_='%d')    
        t.addColumn('score_is', t.feature_id.apply(lambda v: fun(v,d2,1)), format_='%d')    
    else:
        t.addColumn('num_c_by_is', None)    
        t.addColumn('score_is', None)    
    t.addColumn('min_c_by_dli', t.feature_id.apply(lambda v: fun(v,d3,0)), format_='%d')
    t.updateColumn('min_c_db', t.feature_id.apply(lambda v: fun(v, d4, 0)), format_='%d')
    t.updateColumn('max_c_db', t.feature_id.apply(lambda v: fun(v,d4 , 1)), format_='%d')    
    return t


def _select_n_c(t):
    _score_n_c_values(t)
    selected=_evaluate_scoring_and_select_best_scored(t)
    num_c=dict()
    for key, v1, v2, v3, v4, v5 in selected:
            if num_c.has_key(key):
                print 'ogottogott'
            num_c[key]=(v1,v2,v3,v4,v5)
    print 'total count of selected features', len(selected)
    return num_c


def _score_n_c_values(t):
    """ RULES:
        assumption the probility of min_c_by_dli is excluding if not fullfilled
        - is_score:
        num_score_by_is==3: +1
        num_c_by_nl==num_c_by_is: +1 #scoring is adjusted to LTQ-Orbitrap instrument
        num_c_by_is in range(min_c_by_nl, max_c_by_nl): +2  # if linear instrument error small:
                                                            # min_c_by_nl == max_c_by_nl
        num_c_by_is >=min_c: +4 
        num_c_by_is in range(db_min, db_max): +5
        - nl_score:
        num_c_by_nl: 1
        num_c_by_nl in range(min_c_db, max_c_db): +5
        num_c_by_nl==num_c_by_is: +2
        num_c_by_nl >=min_c: +4
        num_c_by_is not in range(min_c_by_nl, max_c_by_nl) +1
        - min_c_score:
        min_c_by_dli in range(db_min, db_max): +5
        (min_c_by_dli > num_c_by_is) & (min_c_by_dli > num_c_by_nl): +6
        min_c_by_dli.in range(min_c_by_nl, max_c_by_nl): +2
        min_c_by_dli==1 & num_c_by_nl ==None & num_c_by_is ==None: min_c_by_dli=0
        
    """
    def fun(v):
        return 0 if v is None else v
        
    t.updateColumn('_is_score', t.num_c_by_is.inRange(t.min_c_db, t.max_c_db).thenElse(5,0))
    t.addColumn('_min',t.min_c_by_nl.apply(fun, filter_nones=False))
    t.addColumn('_max',t.max_c_by_nl.apply(fun, filter_nones=False))
    t.updateColumn('_is_score', t.num_c_by_is.inRange(t._min, t._max).thenElse\
                    (t._is_score + 2, t._is_score))
    same_value=t.num_c_by_is.apply(fun, filter_nones=False)\
                ==t.num_c_by_nl.apply(fun, filter_nones=False)
    not_none=t.num_c_by_is.isNotNone() & t.num_c_by_nl.isNotNone() 
    t.updateColumn('_is_score', (same_value & not_none).thenElse(t._is_score+1, t._is_score))
    t.updateColumn('_is_score', (t.score_is==3).thenElse(t._is_score+2, t._is_score))
    dli_crit=t.num_c_by_is.apply(fun, filter_nones=False)\
                                    >=t.min_c_by_dli.apply(fun, filter_nones=False)
    not_none=t.num_c_by_is.isNotNone() & t.min_c_by_dli.isNotNone() 
    t.updateColumn('_is_score', (dli_crit & not_none).thenElse(t._is_score+4, t._is_score))
    
#    # scoring for nl
    t.updateColumn('_nl_score', t.num_c_by_nl.inRange(t.min_c_db, t.max_c_db).thenElse(5,0))
    t.updateColumn('_nl_score', (t.num_c_by_nl.apply(fun, filter_nones=False)==True).thenElse\
                                (t._nl_score+1, t._nl_score))
    t.updateColumn('_nl_score', (same_value & not_none).thenElse(t._nl_score+1, t._nl_score))
    dli_crit=t.num_c_by_nl.apply(fun, filter_nones=False)\
                                    >=t.min_c_by_dli.apply(fun, filter_nones=False)
    not_none=t.num_c_by_nl.isNotNone() & t.min_c_by_dli.isNotNone() 
    t.updateColumn('_nl_score', (dli_crit & not_none).thenElse(t._nl_score+4, t._nl_score))
    nl_range_crit=t.num_c_by_is.inRange(t._min, t._max)
    is_none=t.num_c_by_is.isNone()  | t.num_c_by_nl.isNone()
    t.updateColumn('_nl_score', (nl_range_crit | is_none).thenElse\
                    (t._nl_score, t._nl_score+1))
                    
#    # scoring for dli:
    t.updateColumn('_dli_score', t.min_c_by_dli.inRange(t.min_c_db, t.max_c_db).thenElse(5,0))
    min_c_is_max=(t.min_c_by_dli.apply(fun, filter_nones=False)\
                    >t.num_c_by_is.apply(fun, filter_nones=False) ) &\
                    (t.min_c_by_dli.apply(fun, filter_nones=False)\
                    >t.num_c_by_nl.apply(fun, filter_nones=False) )
    not_none=(t.num_c_by_is.isNotNone() | t.num_c_by_nl.isNotNone())
    t.updateColumn('_dli_score', (min_c_is_max & not_none).thenElse(t._dli_score+6,t._dli_score))
    min_c_in_nl_range=t.min_c_by_dli.apply(fun, filter_nones=False).inRange(t._min, t._max)
    not_none=t.min_c_by_dli.isNotNone() & t.num_c_by_nl.isNotNone() 
    t.updateColumn('_dli_score', (min_c_in_nl_range & not_none).thenElse\
                    (t._dli_score+2,t._dli_score))
    is_none=t.num_c_by_is.isNone() & t.num_c_by_nl.isNone() 
    is_one=t.min_c_by_dli.apply(fun, filter_nones=False)==1
    t.updateColumn('_dli_score', (is_none & is_one).thenElse(0, t._dli_score))
    t.dropColumns('_min', '_max')

    
def _evaluate_scoring_and_select_best_scored(t):
    """
    """
    scores=zip(t._is_score.values, t._nl_score.values, t._dli_score.values)
    num_cs=zip(t.num_c_by_is.values, t.num_c_by_nl.values, t.min_c_by_dli.values)
    num_cs_min=zip(t.num_c_by_is.values, t.min_c_by_nl.values, t.min_c_by_dli.values)
    num_cs_max=zip(t.num_c_by_is.values, t.max_c_by_nl.values,  t.max_c_db)
    destinated=['by_is', 'by_nl', 'by_dli' ]
    pos_mat=_build_position_mat(scores)
    q_score= _build_column_from_arrays(scores, pos_mat)  
    num_c=_build_column_from_arrays(num_cs, pos_mat)  
    min_num_c=_build_column_from_arrays(num_cs_min, pos_mat)  
    max_num_c=_build_column_from_arrays(num_cs_max, pos_mat)  
    origin=_get_origin(destinated, pos_mat)    
    return zip(t.feature_id.values, num_c, min_num_c, max_num_c, q_score, origin)


def _build_position_mat(scores):
     pos_mat=[]
     for  line in scores:
        max_=np.amax(line)
        if not max_:
            pos_mat.append([0,0,0])
        else:
            select=[]
            for v in line:
                if v:
                    select.append(v/max_)
                else:
                    select.append(0)
            pos_mat.append(select)
     return pos_mat    

    
def _build_column_from_arrays(values_mat, pos_mat):
    selection_mat=_multiply_arrays_with_nones(values_mat, pos_mat)
    return tuple([int(np.sum([v for v in tup if v is not None])) for tup in selection_mat])


def _multiply_arrays_with_nones(a1, a2):
        prod_tmp=np.array(a1, dtype=float)*np.array(a2, dtype=float)
        prod= prod_tmp.astype(object)
        prod[np.isnan(prod_tmp)] = None
        return list(prod)


def _get_origin(destinated, pos_mat):
    selected=[]
    for line in pos_mat:
        if sum(line):
            selected.append([destinated[i] for i,v in enumerate(line) if v][0])
        else:
            selected.append(None)
    return selected    


def _update_samples(samples, final_dic):
    def fun(v, i, dic=final_dic):
        if dic.has_key(v):
            return dic[v][i]
    for sample in samples:
        sample.updateColumn('num_c', sample.feature_id.apply(lambda v: fun(v,0)), format_='%d')
        sample.updateColumn('min_num_c', sample.feature_id.apply(lambda v: fun(v,1)), format_='%d')
        sample.updateColumn('max_num_c', sample.feature_id.apply(lambda v: fun(v,2)), format_='%d')
        sample.updateColumn('q_score', sample.feature_id.apply(lambda v: fun(v,3)), format_='%d')
        sample.updateColumn('origin_of_c_estimation', sample.feature_id.apply(lambda v: fun(v,4)))
        
################################################
#
#  MAIN FUNCTION        
def cc_main(samples, t_idms=None, lin_abs_error=0.03, p_c_source=0.99, max_c_istd=40, config=None):
    """
    """
    if config:
        lin_abs_error=config['instr_linear_error']
        p_c_source=config['c_source_labeling']
        isol_width=config['isol_width']
    t0=_get_t0(samples)
    helper.get_num_isotopes(t0) # since column 'num_isotopes' is missing
    n_c_by_is={}
    if t_idms:
        t_idms=group_idms_features(t_idms, config)
        if not t_idms.hasColumns('area', 'method', 'params'):
            n_cpus=checks._get_n_cpus(t_idms)
            t_idms=checks.enhanced_integrate(t_idms, n_cpus=n_cpus)
        n_c_by_is = estimate_num_c_idms(t0, t_idms, p_c_source=p_c_source, isol_width=isol_width)
    n_c_by_nl = estimate_num_c_nl(t0,  lin_abs_error=lin_abs_error)
    n_c_min = estimate_min_C_mass_traces(samples)
    n_c_db=estimate_C_from_db(samples)
    overview=build_overall_table_from_dicts(n_c_by_nl, n_c_by_is, n_c_min, n_c_db)
    final_dic=_select_n_c(overview)
    _update_samples(samples, final_dic)


def _get_t0(samples):
    t0=None
    for s in samples:
        if s.time.uniqueValue()==0 and s.order.uniqueValue()==0:
            t0=s
    assert t0, 'unlabeled sample is missing or sample order is wrong'
    return t0


def group_idms_features(t_idms, config):
    # extract parameters for feature_gouping
    parameters=dict()
    parameters['delta_mz_tolerance']=config['delta_mz_tol']
    parameters['max_c_gap']=config['max_c_istd']
    _remove_feature_grouping(t_idms)
    # since hires assumes rt vallues of each peak within a feature are unique
    # all features are first decomposed:
    t_idms.replaceColumn('feature_id', t_idms.id)
    return regroup_and_cluster_features([t_idms], parameters)[0]
    

def _remove_feature_grouping(t):
    colnames=['adduct_group', 'possible_adducts', 'carbon_isotope_shift',
              'unlabeled_isotope_shift', 'mass_corr', 'adduct_mass_shift', 'possible_mass']
    remove=[n for n in colnames if t.hasColumn(n)]          
    t.dropColumns(*remove)
    
