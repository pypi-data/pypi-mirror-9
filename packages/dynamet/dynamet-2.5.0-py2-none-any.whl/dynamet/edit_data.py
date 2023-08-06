# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 12:25:25 2013

@author: pkiefer
"""
import glob
import os
import emzed
import objects_check as checks
import numpy as np
import helper_funs as helper
import labeling_plots as plots
from emzed.core.data_types.col_types import Blob


def add_column_by_dict(key, dic):
    if dic.has_key(key):
        return dic[key]


def build_result_table(tables, summary, config, result_path):
    fids=summary['plots_res'][0].keys()
    overview=get_overall_table(tables, fids)
    red=overview_by_collapsing(overview, collaps_cols=["feature_id","adduct_group"],
                                   additional=['z', 'rt', 'mz0', 'min_mz', 'possible_m0', 'num_c'])
    def fun(v,  dic=summary['fcluster_res']):
        return add_column_by_dict(v, dic)
    red.addColumn('fcluster_id', red.feature_id.apply(fun), type_=int, format_='%d', 
                  insertBefore='collapsed')
    def fun1(v,  dic=summary['fit_curve_res']):
        value = add_column_by_dict(v, dic)
        if value:
            return value[0]
    red.addColumn('label_t50_sec', red.feature_id.apply(fun1), type_=float, format_='%.1f', 
                  insertBefore='collapsed')
    def fun1a(v,  dic=summary['fit_curve_res']):
        value = add_column_by_dict(v, dic)
        if value:
            return value[-1]
    red.addColumn('std_label_t50_sec', red.feature_id.apply(fun1a), type_=float, format_='%.1f', 
                  insertBefore='collapsed')
    def fun2(v,  dic=summary['fit_curve_res']):
        if add_column_by_dict(v, dic):
            return add_column_by_dict(v, dic)[1] 
    red.addColumn('c13_fraction_calc', red.feature_id.apply(fun2), type_=float, format_='%.2f', 
                  insertBefore='collapsed')
    def fun2a(v,  dic=summary['fit_curve_res']):
        if add_column_by_dict(v, dic):
            return add_column_by_dict(v, dic)[-2] 
    red.addColumn('std_c13_fraction_calc', red.feature_id.apply(fun2a), type_=float, format_='%.2f', 
                  insertBefore='collapsed')
    def fun3(v,  dic=summary['fit_curve_res']):
        if add_column_by_dict(v, dic):
            return add_column_by_dict(v, dic)[2] 
    red.addColumn('nrmse', red.feature_id.apply(fun3), type_=float, format_='%.2f', 
                  insertBefore='collapsed')
    def fun4(v,  dic=summary['fit_curve_res']):
        if add_column_by_dict(v, dic):
            return add_column_by_dict(v, dic)[3] 
    red.addColumn('fit_model', red.feature_id.apply(fun4), type_=str, 
                  insertBefore='collapsed')
    def fun4a(v,  dic=summary['pool_curve_res']):
        if add_column_by_dict(v, dic):
            return add_column_by_dict(v, dic)[1]
    red.addColumn('pool_t50_sec', red.feature_id.apply(fun4a), type_=float, format_='%.1f', 
                  insertBefore='collapsed')
    def fun4b(v,  dic=summary['pool_curve_res']):
        value = add_column_by_dict(v, dic)
        if value:
            return value[-1]
    red.addColumn('std_pool_t50_sec', red.feature_id.apply(fun4b), type_=float, format_='%.1f', 
                  insertBefore='collapsed')
    def fun5(v,  dic=summary['plots_res']):
        return add_column_by_dict(v, dic[0])
    red.addColumn('dli_plots', red.feature_id.apply(fun5), insertBefore='collapsed')
    def fun6(v, dic=summary['plots_res']):
            return add_column_by_dict(v, dic[1])
    red.addColumn('M0_dilution_plots', red.feature_id.apply(fun6), insertBefore='collapsed')
    def fun7(v,  dic=summary['ident_res']):
        return add_column_by_dict(v, dic)
    red.addColumn('identification_results', red.feature_id.apply(fun7))
    red.renameColumns(collapsed='details')
    cluster_plot=plots.generate_fcluster_plot_from_result_file(red, path=result_path)
    red.addColumn('feature_clustering_plot', cluster_plot, insertBefore='details')
    file_name=save_result(red, result_path)
    config['result']=file_name
    return red


def save_result(result, result_path):
        time_label=helper.time_label()
        name=time_label+'_dynamet_result.table'
        path=os.path.join(result_path, name)
        helper.enhanced_save_table(result, path)    
        return path


def get_overall_table(tables, fids):
    overall=emzed.utils.mergeTables(tables, reference_table=tables[0])
    overall=overall.filter(overall.feature_id.isIn(fids))
    overall=_cleaner(overall)
    return overall
    
    
def _cleaner(table):
    colnames=['adduct_group', 'possible_adducts', 'feature_id', 
               'mz', 'mzmin', 'mzmax', 'z', 'possible_m0', 'rt', 'rtmin', 'rtmax', 
              'fwhm', 'method', 'area', 'rmse', 'params', 'peakmap', 'source', 'mz0', 
              'feature_mz_min', 'time', 'order', 'num_isotopes', 'num_c', 'min_num_c', 'max_num_c', 
              'q_score', 'origin_of_c_estimation', 'mi_fraction', 'mi_frac_corr', 'no_C13', 
              'C13_fraction']
    checks.table_has_colnames(colnames, table)    
    table.addColumn('compound_name', 'enter name manualy', insertBefore='possible_adducts')
    new=table.extractColumns(*colnames)
    new.renameColumns(feature_mz_min='min_mz')
    return new
    

def check_for_intermediate_result(path):
    files=glob.glob(os.path.join(path,"*_step1.table"))
    if len(files):
        names=[os.path.basename(fil) for fil in files]
        names.append("Don't reload")
        numb=emzed.gui.DialogBuilder("load intermediate result")\
        .addChoice("choose file", names)\
        .show()
        if numb!=len(names)-1:
            result=emzed.io.loadTable(files[numb])
            return result.splitBy("source")


def save_intermediate_result(results, path):
    result=emzed.utils.mergeTables(results, force_merge=True)
    assert isinstance(path, str)
    assert os.path.isdir(path), "path for saving is not existing"
    name=helper.time_label()+"_step1.table"
    file_name=os.path.join(path,name)
    result.store(file_name)
    return file_name


def overview_by_collapsing(t, collaps_cols=['feature_id', 'adduct_group'], additional=None):
    reduced=t.collapse(*collaps_cols) 
    if additional:
        for colname in additional:
            def _fun(subt, colname=colname):
                values=subt.getColumn(colname).values
                if True in[isinstance(v, Blob) for v in values]:
                    return values[0]
                if len(set(values))==1:
                    return values[0]
                values=[v for v in subt.getColumn(colname).values if v is not None]
                if len(values):
                    return np.median(values)
            name=colname+'_'
            reduced.addColumn(name, reduced.collapsed.apply(_fun), insertBefore='collapsed')
    return reduced


def _overall_mzrange(table):
    peakmaps=set(table.peakmap.values)
    mz_min1=min([pm.mzRange()[0] for pm in peakmaps])
    mz_min2=max([pm.mzRange()[0] for pm in peakmaps])
    mz_max1=min([pm.mzRange()[-1] for pm in peakmaps])
    mz_max2=max([pm.mzRange()[-1] for pm in peakmaps])
    print mz_min1
    print mz_min2
    assert abs(mz_min1-mz_min2)<1.0, "lower mass range limit not consistent"\
            "in measured data set"
    assert abs(mz_max1-mz_max2)<1.0,  "upper mass range limit not consistent"\
            "in measured data set"            
    return mz_min2, mz_max2


def _cleanup(t):
    def _count(t):
        return t.cid.countNotNone()
    t.dropColumns('mz0__0', 'z__0', 'mass_shift__0')
    helper.removePostfixes(t)
    t.replaceColumn("compound_names", 
                          t.compound_names.apply(lambda v: v[:80]+"..."))
    cleaned=t.collapse('feature_cluster', 'feature_id')  
    cleaned.addColumn('no_of_assigned_compounds', cleaned.collapsed.apply(_count),
                      insertBefore='collapsed')      
    remove_ending(t)                      
    return cleaned    

def remove_ending(t):
    for n in t.getColNames():
        if n.endswith('_'):
            t.renameColumn(n, n[:-1])
        