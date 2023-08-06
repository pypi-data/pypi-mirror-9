# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 18:00:42 2013

@author: pkiefer
"""
import os
import emzed
from emzed.core.data_types import PeakMap, Table
import objects_check as checks
import helper_funs as helper
import numpy as np
import hires

MMU=0.001
here = os.path.dirname(os.path.abspath(__file__))

def peakmaps2feature_tables(ppms, ff_metabo):
    print "building basic feature tables from processed peakmaps..."
    assert isinstance(ff_metabo, dict), "parameters is dictionary comprising all"\
                                        " parameter settings"
    print
    print "finding features with openMS feature finder metabo..." 
    tables=detect_features(ppms, ff_metabo)
    return tables
    

def align_tables(tables, parameters, path, calibrants=None):
    if parameters['rt_alignment']:
        ppms=[t.peakmap.uniqueValue() for t in tables]
        tables_rt_aligned=rt_align_tables(tables, parameters, path)    
        tables_rt_aligned=_update_processing(tables_rt_aligned)
        pms_rt_aligned=[t.peakmap.uniqueValue() for t in tables_rt_aligned]
    #   the quality of rt-alignment can be checked. 
        al=True # in case no calibrants are available rt aligned data set is kept
        if calibrants:
            al, not_al, new_rttol=compare_variability_check(ppms, pms_rt_aligned, calibrants)   
        if new_rttol:
            parameters=_adapt_rttol(parameters, new_rttol)
            align_tables(tables, parameters, path, calibrants)
        if al:
            return  tables_rt_aligned 
        if not_al:
            return  tables
    return tables
        

def _update_processing(tables):
    process='rt_aligned'
    for t in tables:
        pm=t.peakmap.uniqueValue()
        helper.label_peakmap_processing(pm, process)
        t.replaceColumn('peakmap', pm)
    return tables
    
    
def detect_features(items, parameters):
    tables=[]
    for item in items:
        if isinstance(item, Table):
            assert item.hasColumns('peakmap', 'source', 'unique_id')
            pm=item.peakmap.uniqueValue()
            pm.meta['source']=item.source.uniqueValue()
            unique_id=item.unique_id.uniqueValue()
        elif isinstance(item, PeakMap):
            pm=item
            unique_id=pm.uniqueId()
        else:
            assert False, 'item must be either of type PeakMap or Table'
        t=emzed.ff.runMetaboFeatureFinder(pm, **parameters)
        t.updateColumn("source", t.peakmap.uniqueValue().meta["source"])
        t.addColumn('unique_id', unique_id, format_=None)
        title=t.peakmap.uniqueValue().meta["source"].split(".")[0]
        t.title=title
        tables.append(t)
    return tables

    
def regroup_and_cluster_features(tables, parameters):
    max_c_gap=parameters['max_c_gap']
    mz_tolerance=parameters['delta_mz_tolerance']
    mean_hwhm=helper.determine_fgrouper_rttol(tables)
    result=[]
    for i,t in enumerate(tables):
        print 'sample %s'%t.title
        print '%d out of %d' %(i, len(tables)) 
        n_cpus=checks.get_n_cpus(t)
        t=emzed.utils.integrate(t, 'max', n_cpus=n_cpus)
        t=hires.feature_regrouper(t, max_c_gap=max_c_gap, rt_tolerance=mean_hwhm, 
                                  mz_tolerance= mz_tolerance)
         # since code uses column feature_id orginating from ff_metabo we replace column 
         # feauture_id  by isotope_cluster_id and remove the latter
        print 'done'
        print 'grouping adducts.....'
        hires.assign_adducts(t)
        _cleanup_adduct_assignment(t)
        _cleanup_feature_regrouping(t)
        _add_adduct_mass_shifts(t)
        calculate_mass(t)
        print 'done'
        result.append(t)
    return result
  
  
def _cleanup_feature_regrouping(t):
    t.replaceColumn('feature_id', t.isotope_cluster_id)
    t.dropColumns('isotope_cluster_id')


def _cleanup_adduct_assignment(t):
    # remove redundant entruies in column unlabeled_mass_shifts
    colnames=['unlabeled_isotope_shift', 'mass_corr']
    for name in colnames:
        if name.startswith('un'):
            expr=t.getColumn(name).contains('-').thenElse(None, t.getColumn(name))
        else:
            expr=(t.getColumn(name)<0).thenElse(None, t.getColumn(name))
        t.replaceColumn(name, expr)

        
def build_adduct_mass_shift_dict(mode='-'):
    assert mode in ['-', '+']
    t=emzed.adducts.negative.toTable()  
    values=zip(t.adduct_name.values, t.mass_shift.values)
    return {key:value for key, value in values}


def _add_adduct_mass_shifts(t, dic=None, mode='-'):
    required='possible_adducts'
    assert t.hasColumns(required), 'column %s is missing' %required
    if t.hasColumn('adduct_mass_shift'):
        t.dropColumns('adduct_mass_shift')
    if not dic:
        dic=build_adduct_mass_shift_dict(mode=mode)
    _possible_adducts_to_tuples(t)
    def fun(v, dic=dic):
        shifts=[]
        for x in v:
            if dic.has_key(x):
                shifts.append(dic[x])
        return tuple(shifts)
    t.addColumn('adduct_mass_shift', t.possible_adducts.apply(fun), insertBefore='mz', type_=None)
    
    
def _possible_adducts_to_tuples(t):
    required='possible_adducts'
    assert t.hasColumns(required), 'column %s is missing' %required
    def fun(v):
        adducts=v.split(', ')
        adducts=[v.replace(' ', '') for v in adducts]
        return tuple(adducts)
    t.replaceColumn('possible_adducts', t.possible_adducts.apply(fun))


def calculate_mass(t):    
    required=['mz', 'z', 'adduct_mass_shift']
    checks.table_has_colnames(required, t)
    def fun(table, row, new_col_name):
        # posssible mass shifts
        values=table.getValue(row, 'adduct_mass_shift')
        if values is not None and all(values):
            x=[]
            for v in values:
                x.append(table.getValue(row, 'mz') * table.getValue(row, 'z')-v)
            return tuple(x)
    if t.hasColumn('possible_mass'):
        t.dropColumns('possible_mass')
    t.addColumn('possible_mass', fun, insertBefore='mz')
    
    
def _adapt_rttol(parameters, rttol):
    feature_extr=parameters['feature_extraction']
    feature_extr['rttol']=rttol

    
def _clean_up(t):
    """
    """
    t.addColumn('fid_ffmetabo', t.feature_id, format_=None)
    t.replaceColumn('feature_id', t.isotope_cluster_id)
    t.dropColumns('isotope_cluster_id')
    
   
def mz_align_peakmaps(peakmaps, parameters, path=None):
    """
    """
    p=parameters
    calib_table=parameters['mz_calib_table']
    tables=[pm2table(calib_table, pm) for pm in peakmaps]
    aligned=[]
    for t in tables:
        print "aligning peakmap %s ..." %t.source.uniqueValue()
        t=emzed.align.mzAlign(t, calib_table, tol=p['mztol'], minR2=p['minR2'], 
                              interactive=p['interactive'], destination=path)
        aligned.append(t)
    pms_aligned=[t.peakmap.uniqueValue() for t in aligned]
    return pms_aligned
    

def pm2table(calibration_table, peakmap, mztol=10*MMU):
    """
    """
    assert isinstance(peakmap, PeakMap), 'peakmap is not of type PeakMap'
    t=calibration_table.copy()
    required=["mzmin", "mzmax", "rtmin","rtmax"]
    checks.table_has_colnames(required, t)
    supportedPostfixes=t.supportedPostfixes(required)
    for pstfx in supportedPostfixes:
         t.updateColumn("peakmap"+pstfx, peakmap)
    t=emzed.utils.integrate(t, 'emg_exact', n_cpus=8)
    for pstfx in supportedPostfixes:
         # update format of rtmin and rtmax
         t.updateColumn("rtmin"+pstfx, t.getColumn("rtmin"+pstfx),
                              format_="'%.2fm' %(o/60.0)"+t.title)
         t.updateColumn("rtmax"+pstfx, t.getColumn("rtmax"+pstfx),
                              format_="'%.2fm' %(o/60.0)")
         t.updateColumn('rt'+pstfx, t.getColumn("params"+pstfx).apply(lambda v: v[1]))
         t.addColumn("source"+pstfx, peakmap.meta['source'])
    t.updateColumn("polarity", peakmap.polarity)
    emzed.utils.recalculateMzPeaks(t)
    return t
    
    
def rt_align_tables(tables, config, path):
    """ 
    """
    print 'retention time alignment using pose clustering...' 
    p=config
    destination=os.path.join(path, 'temp')
    os.mkdir(destination)
    aligned=emzed.align.rtAlign(tables, refTable=p['ref'], destination=destination, 
                                maxRtDifference=p['rt_diff'], maxMzDifference=p['mz_diff'])
    helper.remove_files_from_path(destination)
    os.removedirs(destination)
    print 'Done'
    return aligned
    
def compare_variability_check(pms_before, pms_after, rt_calib, rttol=25, f=2):
    """The retention time variationis an important mean to decide whether rt alignment improves
        rt variation or not
    """
    # building tables with calibration peaks before rt alignment
    tables_before=[pm2table(rt_calib, pm) for pm in pms_before]
    rt_para_before=check_rt_variability(tables_before)
    # building tables with calibration peaks after rt alignment
    tables_after=[pm2table(rt_calib, pm) for pm in pms_after]
    rt_para_after=check_rt_variability(tables_after)
    rt_var_before=[rt_para_before[key][1] for key in rt_para_before.keys()]
    rt_var_after=[rt_para_after[key][1] for key in rt_para_after.keys()]
    rt_diff=[]
    for key in rt_para_before.keys():
        rt_diff.append(rt_para_before[key][1]-rt_para_after[key][1])
    # cases:
    # 1. rt alignment general improves the result and variation < rtttol
    if sum(rt_diff)>0:
        if all(rt_var_after)<rttol:
            return True, False,  None
        elif all(rt_var_before)<rttol:
            return False, True, None
        if max(rt_var_after)<f*rttol:
            rttol=max(rt_var_after)
            print "WARNING: rt tolerance was not obtained for calibraiton peaks !\n"\
            "The values is automatically increased to the maximal observed difference %s.\n"\
            "You can try adapting parameters of alignment tool" %rttol
            return False, True, rttol
        elif max(rt_var_before)<f*rttol: 
            rttol=max(rt_var_before)
            print "WARNING: rt tolerance was not obtained for calibraiton peaks !\n"\
            "The values is automatically increased to the maximal observed difference %s.\n"\
            "You can try adapting parameters of alignment tool" %rttol
            return True, False, rttol
        else:
            assert True, 'given data set does not fullfill the maximal rt tolerance criterium \n'\
            "Try to adapt the rt alignment parameters or check your files for critivial sample(s)"
    #2. rt alignment does not reduce peak variability  
    if sum(rt_diff)<=0:
        if all(rt_var_before)<rttol:
            return True, False, None
        elif all(rt_var_after)<rttol:
            return False, True, None
        elif max(rt_var_before)<f*rttol: 
                    rttol=max(rt_var_before)
                    print "WARNING: rt tolerance was not obtained for calibraiton peaks !\n"\
                    "The values is automatically increased to the maximal observed difference %s.\n"\
                    "You can try adapting parameters of alignment tool" %rttol
                    return True, False, rttol
        elif max(rt_var_after)<f*rttol:
                rttol=max(rt_var_after)
                print "WARNING: rt tolerance was not obtained for calibraiton peaks !\n"\
                "The values is automatically increased to the maximal observed difference %s.\n"\
                "You can try adapting parameters of alignment tool" %rttol
                return False, True, rttol
        else:
            assert False, 'given data set does not fullfill the maximal rt tolerance criterium \n'\
            "Try to adapt the rt alignment parameters or check your files for critivial sample(s)"
 
   
def check_rt_variability(tables):
    comp=dict()
    for t in tables:
        keys=zip(t.id.values, t.z.values)
        values=t.rt.values
        for i,_ in enumerate(keys):
            if comp.has_key(keys[i]) and values[i]>0:
                comp[keys[i]].append(values[i])
            elif values[i]>0:
                comp[keys[i]]=[values[i]]
    for key in comp.keys():
        comp[key]=(np.mean(comp[key]), np.max(comp[key])-np.min(comp[key]))
    return comp


    
    


