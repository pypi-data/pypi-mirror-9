# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 14:38:59 2014

@author: pkiefer
"""
import emzed
import numpy as np
from scipy import stats
import hires
import objects_check as checks
from peakmaps2feature_tables import _add_adduct_mass_shifts as adduct_mass_shifts
import helper_funs as helper


def build_reference_table(tables, isol_width=0.003, rel_min_area=0.01, max_c_gap=10,
                          parameters=None):
    """ Samples must be orderd by labeling incororation time.
    """
    tables_requirements(tables)
    # define variables
    if parameters:
        isol_width=parameters['isol_width']
        rel_min_area=parameters['rel_min_area']
        max_c_gap=parameters['max_c_gap']
    fid_to_maxmzid={}
    multiple=['mz', 'area']
    single=['rt']
    ref_mltpl='mz_id'
#    ref=None
    print "Building reference Table comprising common and unique features overall samples..."
    rttol=get_typ_rt_var(tables)
    ref=initialize_ref_table(tables, isol_width, rttol, rel_min_area)
    # for better representation of rt overall samples feature_rt_values are collected 
            # in fid_rt_dict and rt values of features in ref is updated by median rt values after 
            # each table comparison
    fid_to_maxmzid = _add_mz_id(ref, fid_to_maxmzid = fid_to_maxmzid)    
    collection=collect_column_values(ref, single, ref_single='feature_id',
                                             multiple_values_cols=multiple, 
                                             ref_multi=ref_mltpl)
    subset=[t for t  in tables if t.time.uniqueValue()>0]
    for t in subset:
        print 'extracting features of sample %s...' %t.source.uniqueValue()
        t=prefilter_sample(t, rel_min_area)
        additional, new, matches =select_candidates(ref, t, rttol, isol_width)
        fid_to_maxmzid = _add_mz_id(additional, fid_to_maxmzid = fid_to_maxmzid)
        fid_to_maxmzid = _add_mz_id(new, fid_to_maxmzid = fid_to_maxmzid)
        collection=collect_column_values(matches, single, multiple_values_cols=multiple, 
                                         ref_multi=ref_mltpl, collection=collection)
        collection=collect_column_values(new, single, multiple_values_cols=multiple, 
                                         ref_multi=ref_mltpl, collection=collection)
        collection=collect_column_values(additional, single, multiple_values_cols=multiple, 
                                         ref_multi=ref_mltpl, collection=collection)
        ref=emzed.utils.mergeTables([ref, additional, new], reference_table=ref)
        # replace rt, mz values, by corresponding median values from collection
        _update_ref_columns(ref, collection)
    ref=remove_rare_fids(ref, collection['rt'], min_matches=2)
    ref.addEnumeration()
    print 'len of ref', len(ref)
    assert len(ref)>0, 'no features could be identified!'
    # reduce hwhm to selected peaks
    f_rttol=rt_isolation_width([ref])    
    parameters['ref_table_score']=check_ref_rttol(collection, f_rttol)
    parameters['rt_tol']=f_rttol
    ref=hires.feature_regrouper(ref, max_c_gap=max_c_gap, rt_tolerance=f_rttol)
    hires.assign_adducts(ref)
    adduct_mass_shifts(ref)
    ref=_get_missing_mz0(ref, tables[0], isol_width=isol_width, rttol=f_rttol)
    # hires might multiply features. However feature mzmin might differ for features, and mz0
    # and feature_mz_min must be adapted
    return cleanup_ref(ref, isol_width)


def tables_requirements(tables):
    required=['feature_id', 'mz', 'rt', 'area', 'z', 'source', 'unlabeled_isotope_shift',
              'intensity']
    not_none=['feature_id', 'mz', 'rt', 'area', 'source', ]
    for t in tables:
        checks.table_has_colnames(required, t)
        assert len(t)>0, 'table is empty!' 
        assert len(set(list(t.source.values))) == 1
        colnames=[name for name in t.getColNames()]
        for name in colnames:
            value=len(t)-t.getColumn(name).countNone()
            print value
            if name in not_none:
                assert value>0, 'only None values in column %s' %name
            
            
def _build_colname_type_dict():
    """ defines column Types of reference tables
    """
    name2type=dict()
    name2type['id']=int
    name2type['adduct_group']=int
    name2type['adduct_mass_shift']=tuple
    name2type['possible']=tuple
    name2type['num_isotopes']=int
    name2type['feature_id']=int
    name2type['mz']=float
    name2type['rt']=float
    name2type['mz0']=float
    name2type['area']=float
    name2type['mz_id']=int
    name2type['feature_mz_min']=float
    name2type['source']=str
    name2type['z']=int
    return name2type


def update_ref_coltypes(t):
    colnames=[n for n in t.getColNames()]
    name2type=_build_colname_type_dict()
    for name in colnames:
        if name2type.has_key(name):
            t.replaceColumn(name, t.getColumn(name), type_=name2type[name])


def initialize_ref_table(tables, isol_width, rttol, rel_min_area):
    print 'initializing reference table...'
    #1. get all samples with natural labeling
    t0_tables=[initial_ref(prefilter_sample(t, rel_min_area)) for t in tables if t.time.uniqueValue()==0]
    ref=t0_tables[0]
#    collect_rt={p[0]:p[1] for p in zip(ref.feature_id.values, ref.rt.values)}
    
    colnames=[n for n in ref.getColNames()]
    # if more than 1 t0 table...
    if len(t0_tables)>0:
        for t0 in t0_tables[1:]:
    #        t=prefilter_sample(t, rel_min_area)
            #find common features
            merged=t0.leftJoin(ref, t0.mz.approxEqual(ref.mz, isol_width) & 
                    t0.rt.inRange(ref.rt-rttol/2.0, ref.rt + rttol/2.0) & (t0.z == ref.z))
            # select different features
            selected=merged.filter(merged.feature_id__0==None)
            # remove all columns from ref table
            selected=selected.extractColumns(*colnames)
            # exclude not unique feature_id values:
            selected.replaceColumn('feature_id', selected.feature_id+len(ref)+len(t0))
            # enlarge ref by selected
            ref=emzed.utils.mergeTables([ref, selected])
    assign_consistent_fid(ref)
    helper.update_mz0(ref)
    print 'done'
    return ref
            
        
    
def initial_ref(t):
    cand=t.filter((t.z>0))
    #determine monoisotopic peaks of natural labeled features since t[0] = t0
    cand.updateColumn('mz0', cand.mz.min.group_by(cand.feature_id), type_=float)
    cand.updateColumn('feature_mz_min', cand.mz.min.group_by(cand.feature_id), type_=float)
    assign_consistent_fid(cand)
    return _extract_ref_cols(cand)


def prefilter_sample(table, rel_min_area):
    required=['feature_id', 'area', 'unlabeled_isotope_shift']
    checks.table_has_colnames(required, table)
    t=table.copy()
    t.addColumn('_max',t.area.max.group_by(t.feature_id))
    t.addColumn('_rel', t.area*1.0/t._max*1.0, type_=float)
    t.addColumn('mz0', None, type_=float)
    t.addColumn('feature_mz_min', None, type_=float)
    t.addColumn('mz_id', None, type_=int)         
    # remove all peaks not fullfilling the minimal area criterium
    # and all peaks were isotope shift cannot be explained by 13C
    t=t.filter(t._rel>rel_min_area)
    t=t.filter(t.unlabeled_isotope_shift.isNone())
    t.dropColumns('_rel', '_max')
    return t


def cleanup_ref(ref, isol_width):
    # remove features with single peaks (z==0) due to repeated feature grouping
    ref=ref.filter(ref.z>0)
    ref.updateColumn('feature_mz_min', ref.mz.min.group_by(ref.isotope_cluster_id))
    _replace_mz0(ref)
    ref=ref.filter(ref.mz-ref.feature_mz_min+isol_width>=0)
    ref.replaceColumn('feature_id', ref.isotope_cluster_id)
    helper.get_num_isotopes(ref)
    ref=remove_redundance(ref)
    ref.addEnumeration()
    helper.get_monoisotopic_mass(ref, insert_before='num_isotopes')
    return ref


def _replace_mz0(ref, delta=0.05):
    """ comments: feature_mz_min is in set(mz0.values): the feature has been recomposed and mass
        peaks of a feature with different mzmin were added.  Choose mz0 corresponding
        to feature_mz_min
    """
    icid_2_mz0=helper.extract_dict_from_table(ref, 'isotope_cluster_id', 'mz0')
    icid_2_fmzmin=helper.extract_dict_from_table(ref, 'isotope_cluster_id', 'feature_mz_min')
    def _replace(v, dic1=icid_2_mz0, dic2=icid_2_fmzmin, delta=delta):
        mz0_values=dic1[v]
        assert len(dic2[v])==1 # unique feature_mz_min
        fmzmin=dic2[v][0]
        for mz0 in mz0_values:
            if mz0:
                if abs(fmzmin-mz0)<delta:
                    return fmzmin
        return -1.0 # fix type_error
    ref.replaceColumn('mz0', ref.isotope_cluster_id.apply(_replace), type_=float)
    #fix type_error since mz0 >= 0
    ref.replaceColumn('mz0', (ref.mz0==-1.0).thenElse(None, ref.mz0))
    
    
def remove_redundance(ref, collapse_names=None):
    if not collapse_names:
        collapse_names=['isotope_cluster_id', 'adduct_group', 'adduct_mass_shift',
                        'possible_adducts', 'feature_mz_min', 'rt', 'mz0', 'z', 'num_isotopes']
    delta_c=emzed.mass.C13-emzed.mass.C12
    def fun(table, row, new_col_name):
        return (table.getValue(row, 'isotope_cluster_id'), table.getValue(row, 'num_isotopes'))
    ref.addColumn('_select', fun)
    # if several isotopes within same feature (this is a consequence of rttol!, peak tailing,...)
    # keep the one with hinghest area
    before=len(ref)
    ref.addColumn('a_max', ref.area.max.group_by(ref._select))
    ref=ref.filter(ref.area==ref.a_max)
    ref.addColumn('rt_', ref.rt.median.group_by(ref.isotope_cluster_id))
    ref.replaceColumn('rt', ref.rt_)
    ref.dropColumns('a_max', '_select', 'rt_')
    print 'removed %d `side` peaks' %(before - len(ref))
    # constrain 2: remove features with single peaks
    before=len(ref)
    ref.addColumn('_len', ref.isotope_cluster_id.len.group_by(ref.isotope_cluster_id))
    ref=ref.filter(ref._len>1)
    ref.dropColumns('_len')
    print 'removed %d features with only 1 peak' %(before - len(ref))
    ##################
    # COLLAPSE Table by command collapse to remove doubles and recalculate mz values based on 
    # labeled C mass shift time column 'num_isotopes'
    before=len(ref)
    ref=ref.collapse(*collapse_names)
    print 'removed %d `double` peaks' %(before - len(ref))
    ref=ref.extractColumns(*collapse_names)
    ref.addColumn('mz', ref.feature_mz_min+(ref.num_isotopes*delta_c)/(ref.z*1.0))
    ref.renameColumns(isotope_cluster_id='feature_id')
    ref=ref.filter(ref.feature_id.len.group_by(ref.feature_id)>1)
    return ref
    

def _add_mz_id(t, fid_to_maxmzid=None):
    # mz_id needed for collecting feature mz values.
    if not fid_to_maxmzid:
        fid_to_maxmzid={}
    def get_mzid(v,dic=fid_to_maxmzid):
        if not dic.has_key(v):
            dic[v]=0
        value=dic[v]
        dic[v]+=1
        return value
    if t.hasColumn('mz_id'):
        t.replaceColumn('mz_id', t.mz_id.ifNotNoneElse(t.feature_id.apply(get_mzid)), type_=int)
    else:
        t.addColumn('mz_id', t.feature_id.apply(get_mzid), type_=int, format_='%d')    
    return fid_to_maxmzid
        
        
def assign_consistent_fid(t, fid_t=None):
    if fid_t!=None:
        max_fid=fid_t+1
    else:
        max_fid=0
    fids=list(set(t.feature_id.values))
    assign=zip(fids, range(max_fid, len(fids)+max_fid))
    def fun(v, fid=assign):
                for f in fid:
                    if v==f[0]:
                        return f[1]
    t.replaceColumn('feature_id', t.feature_id.apply(fun))
    

def _extract_ref_cols(t, ref_cols=None):
    if not ref_cols:
        ref_cols=['feature_id', 'rt', 'mz', 'mz0', 'feature_mz_min', 'z', 'area', 'mz_id', 'fwhm']
        ref=t.extractColumns(*ref_cols)
        update_ref_coltypes(ref)
    return ref
    

##########################################################

def collect_column_values(t, single_value_cols, ref_single='feature_id',
                          multiple_values_cols=None, ref_multi=None, collection=None):
    """ column values varying from sample to sample e.g. mz, rt are collected for averaging
    """
    if not collection:
        collection=dict()
    if ref_single:
        _update_collection(t, t.getColumn(ref_single).values, single_value_cols, collection)
    if multiple_values_cols:
        keys=zip(t.getColumn(ref_single).values, t.getColumn(ref_multi).values)
        _update_collection(t, keys, multiple_values_cols, collection)
    return collection


def _update_collection(t, keys, colnames, collection):
    for colname in colnames:
        values=t.getColumn(colname).values
        pairs=zip(keys, values)
        
        median_pairs=[]
        for key in set(keys):
            median=round(float(np.median([p[1] for p in pairs if p[0]==key])),5)
            median_pairs.append((key,median))
        if collection.has_key(colname):
                collection[colname]=fid_col_dict(median_pairs, fid_t=collection[colname])
        else:
            collection[colname]=fid_col_dict(median_pairs)


def fid_col_dict(pairs, fid_t=None):
    if not fid_t:
        fid_t=dict()
    for key, value in pairs:
#        key=int(key)
        if fid_t.has_key(key):
            fid_t[key].append(value)
        else:
            fid_t[key]=[value]
    return fid_t
    
#################################################
    
def select_candidates(ref, t, rttol, isol_width):
    if len(t):
        fid_t=ref.feature_id.max()
        cand=t.join(ref, t.rt.inRange(ref.rt-rttol/2.0, ref.rt+rttol/2.0) &\
                                 t.mz.approxEqual(ref.mz, isol_width) &\
                                 ((t.z==ref.z) | (t.z==0))&\
                                 (t.mz.min.group_by(t.feature_id)-ref.feature_mz_min+isol_width>=0)) 
                                 # sample with lowest labeling determines feature_mz_min
        if len(cand):
            cand.replaceColumn('mz0', cand.mz0__0)
            cand.replaceColumn('feature_mz_min', cand.feature_mz_min__0)
            matches=same_peaks(cand)
            update_ref_coltypes(matches)
            additional_peaks=additional_peaks_of_existing_ref_features(cand, t, isol_width=isol_width)
            update_ref_coltypes(additional_peaks)
            new=new_features(cand, t)
            assign_consistent_fid(new, fid_t=fid_t)
            update_ref_coltypes(new)
#            new=_extract_ref_cols(new)
            return additional_peaks, new, matches
        else:
            new=initial_ref(t)
            new=_extract_ref_cols(new)
            assign_consistent_fid(new, fid_t=fid_t)
            return None, new, None
    return None, None, None


def same_peaks(cand, postfix='__0'):
        matches=cand.copy()
        colnames=['feature_id', 'z', 'mz_id']
        for colname in colnames:
            _replace(matches, colname, postfix)
        return _extract_ref_cols(matches)

    
def _replace(t, colname, postfix):
    """ inplace
    """
    t.replaceColumn(colname, t.getColumn(colname+postfix))
    t.dropColumns(colname+postfix)
    
    
def additional_peaks_of_existing_ref_features(cand, t, isol_width=0.003):
    if len(cand):
        additional=t.filter(t.feature_id.isIn(cand.feature_id.values))
        pairs=zip(cand.feature_id.values, cand.id.values)
        a=additional
        def fun(table, row, new_col_name):
            return (table.getValue(row, 'feature_id'), table.getValue(row, 'id'))
        a.addColumn('pairs', fun)
        additional=a.filter(~a.pairs.isIn(pairs))
        pairs=set(zip(cand.feature_id.values, cand.feature_id__0.values))
        dic={p[0] : p[1] for p in pairs}
        def _replace(v, dic=None):
            if dic.has_key(v):
                return dic[v]
        additional.replaceColumn('feature_id', additional.feature_id.apply(lambda v: _replace(v,dic=dic)),
                                 type_=int)
        dic=_build_z_dict(cand)
        additional.replaceColumn('z', additional.feature_id.apply(lambda v: _replace(v, dic=dic)),
                                 type_=int)
        additional=apply_mz_min_constrain(additional, 'feature_mz_min', isol_width)
        return _extract_ref_cols(additional)


def _build_z_dict(t):
    pairs=zip(t.feature_id__0.values, t.z__0.values)
    pairs=set([p for p in pairs if p[1]>0])
    return {p[0] : p[1] for p in pairs}


def apply_mz_min_constrain(t, mz_min_col, isol_width):
    t.addColumn('_mztol', isol_width)
    def _select(table, row, new_col_name):
        if table.getValue(row, mz_min_col)!=None:
            value = table.getValue(row, 'mz')-table.getValue(row, mz_min_col)\
                + table.getValue(row, '_mztol')
            if value >=0:
                return True
            else:
                return False
        else:
            return True
    t.addColumn('_select', _select)
    t=t.filter(t._select==True)
    t.dropColumns('_select', '_mztol')
    return t


def new_features(cand, t):
    if len(cand):
        new = t.filter(~t.feature_id.isIn(cand.feature_id.values) & (t.z>0))
        new.replaceColumn('feature_mz_min', new.mz.min.group_by(new.feature_id), type_=float)
    return _extract_ref_cols(new)

    
def _update_ref_columns(ref, collection):
    _update_tuple_id(ref, 'id_')
    for column in collection.keys():
        dic=dict()
        for id_ in collection[column].keys():
            if column=='area':
                value=sum(collection[column][id_])
            else:
                value=round(float(np.median(collection[column][id_])),5)
            dic[id_]=value
        def _replace(v, dic=dic):
            if dic.has_key(v):
                return dic[v]
        if all(isinstance(key, tuple) for key in dic.keys()):
            ref.replaceColumn(column, ref.id_.apply(_replace))
        elif all(isinstance(key, int) for key in dic.keys()):
            ref.replaceColumn(column, ref.feature_id.apply(_replace))
        else:
            assert False, 'Problems in _update_ref_columns'
    update_ref_coltypes(ref)
    ref.dropColumns('id_')


def _update_tuple_id(t, colname):
    def fun(table, row, new_col_name):
        return (table.getValue(row, 'feature_id'), table.getValue(row, 'mz_id'))
    t.addColumn(colname, fun)

  
def remove_rare_fids(t, fid_to_matches, min_matches=2):
    """ Removes all features from sample with < min_matches over all
        samples. fid_to_matches values can be a list where len(list) is equal to
        the number of matches in samples or an integer with number of matches  
    """  
    assert isinstance(fid_to_matches, dict)
    def _help(fid, dic=fid_to_matches, min_=min_matches):
        if dic.has_key(fid):
            if isinstance(dic[fid], list):
                value=len(dic[fid])
            else:
                assert isinstance(dic[fid], int)
                value=value=dic[fid]
            if value>=min_:
                return True
        return False
    t1=t.copy()
    t1.addColumn('_fullfills', t1.feature_id.apply(_help))
    t1=t1.filter(t1._fullfills==True)
    t1.dropColumns('_fullfills')
    return t1
    
def _get_missing_mz0(ref, t0, isol_width=0.003, rttol=25):
    t=t0.filter(t0.z==0)
    colnames=[name for name in ref.getColNames()]
    amended=ref.leftJoin(t, t.mz.approxEqual(ref.feature_mz_min, isol_width) \
                        & t.rt.inRange(ref.rt-rttol/2.0, ref.rt+rttol/2.0))
    amended.replaceColumn('mz0', ((amended.mz0.isNone()==True) & \
                                    (amended.mz__0.isNotNone()==True)).thenElse\
                                    (amended.feature_mz_min, amended.mz0), type_=float)
    return amended.extractColumns(*colnames)


def get_ref_rt_var(collection):
    """ calculates rt deviations feature-wise for all features detected in at least
    3 samples and returns list
    """
    # extract rt values:
#    variability=[]
    rt_var=[]
#    num=0
    values=collection['rt'].values()
    for value in values:
        if len(value)>3:
#            var=[(v-np.mean(value))**2 for v  in value]
            val=[float(v-np.mean(value)) for v  in value]
#            num+=len(var)
#            variability.extend(var)
            rt_var.extend(val)
    return rt_var #, 2.576*np.sqrt(sum(variability))/num


def check_ref_rttol(collection, rttol):
    rt_var= get_ref_rt_var(collection)
    quality=stats.percentileofscore(rt_var, rttol)
    if quality<90:
        print 'WARNING: high variability on retention time observed'
        return quality, 'critical'
    return quality, 'good'
    

def rt_isolation_width(tables):
    """ returns 0.5 * (90% percentile) of all fwhm values from all tables as rttol value
    """
    fwhms=[]
    for t in tables:
        fwhms.extend(t.fwhm.values)
    return 0.5* stats.scoreatpercentile(fwhms, 90)

    
def get_typ_rt_var(tables, mztol=0.003):
    """ selects top 20 intensities and determines rt difference of identical mz traces in different 
    samples. Output is the 76% Quantile of observed rt differences
    """
    print 'determine typical rt variation'
    top20=[]
    for t in tables:
        # select top 20 biggest peaks
        top20.append(t.filter(t.intensity>=stats.scoreatpercentile(t.intensity.values,80)))
    # join mass traces
    t0=top20[0]
    delta_ts=[]
    rttol=rt_limit(tables)
    for t in top20[1:]:
       common=t0.join(t, t0.mz.approxEqual(t.mz, mztol) & t.rt.inRange(t0.rt-rttol, t0.rt+rttol))
       common.addColumn('delta_t', (common.rt-common.rt__0).apply(abs), format_='%.5f')
       # in case of multiple hits select the one with smallest diff
       common.addColumn('min_delta', common.delta_t.min.group_by(common.feature_id))
       common=common.filter(common.delta_t==common.min_delta)
       delta_ts.extend(common.delta_t.values)
    print stats.scoreatpercentile(delta_ts, 75)
    return stats.scoreatpercentile(delta_ts, 75)

    
def rt_limit(tables, percent_runtime=10):
    return max([t.rt.max() for t in tables])*percent_runtime/100.0           
    




        