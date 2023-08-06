# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 11:19:14 2014

@author: pkiefer
"""
import emzed
import os
import helper_funs as helper
from carbon_count import cc_main
from pacer import  LocalCacheBuilder
from peakmap_processing import process_peakmaps
from peakmaps2feature_tables import peakmaps2feature_tables
from peakmaps2feature_tables import align_tables, regroup_and_cluster_features
from global_features_grouper import extract_global_features
from carbon_labeling import get_feature_carbon_labeling
from data_analysis import main_data_analysis
from edit_data import build_result_table

def setup_wf(config):
    cache=LocalCacheBuilder(os.path.join(config['project_path'],'cache'))
    def set_origin(what, origin):
        what.meta["_origin"] = origin
        return what

    cache.register_handler(emzed.core.Table,
                           lambda t: t.uniqueId(),
                           ".table",
                           emzed.io.loadTable,
                           emzed.io.storeTable,
                           lambda t: t.meta.get("_origin", ""),
                           set_origin)

    cache.register_handler(emzed.core.PeakMap,
                           lambda t: t.uniqueId(),
                           ".mzXML",
                           emzed.io.loadPeakMap,
                           emzed.io.storePeakMap,
                           lambda pm: pm.meta.get("_origin", ""),
                           set_origin)

    def load_peakmaps(config):
        return [emzed.io.loadPeakMap(n) for n in config['project_data']['peakmaps']]
        
        
    def load_int_std(config):
        if config['project_data']['internal_standard']:
            return emzed.io.loadPeakMap(config['project_data']['internal_standard'])

    def build_calibration_table(config):
        dic=config['feature_extraction']['alignment']
        assert dic.has_key('mz_calib_table')
        # key 'mz_calib_table' is set to None if mass calibration is not included
        if dic['mz_calib_table']:
            t=helper.dict_to_table(dic['mz_calib_table'])
            t.addColumn('mzmin', t.mz_hypot-dic['mztol'])
            t.addColumn('mzmax', t.mz_hypot+dic['mztol'])
            return t
###########################################################################            
 # FEATURE EXTRACTION

    @cache
    def _process_peakmap(peakmap, pm_process, alignment, calib_table):
        return process_peakmaps([peakmap], pm_process, alignment, calib_table)[0]

    def _process_peakmaps(peakmaps, fe, calib_table):
        pm_process=fe['peakmap_processing']
        alignment=fe['alignment']
        return [_process_peakmap(pm, pm_process, alignment, calib_table) for pm in peakmaps]
    
    @cache 
    def _peakmap2feature_tables(ppm, ff_metabo):
        return peakmaps2feature_tables([ppm], ff_metabo)[0]
    
    def _peakmaps2feature_tables(ppms, config):
        ff_metabo=config['feature_extraction']['ff_metabo']
        return [_peakmap2feature_tables(ppm, ff_metabo) for ppm in ppms]
    
    @cache
    def _align_tables(tables, config, path, calibrants):
        return align_tables(tables, config, path, calibrants)
        
    @cache   
    def _regroup_and_cluster_feature(table, fe) :
        return regroup_and_cluster_features([table], fe)[0]
    
    def _regroup_and_cluster_features(tables, config):
        fe=config['feature_extraction']
        return [_regroup_and_cluster_feature(t, fe) for t in tables]
    
    @cache
    def _extract_global_features(dli_samples, group, sample_order):
        return extract_global_features(dli_samples, group, sample_order)
########################################################################     
# FEATURE PROCESSING
    @cache
    def _carbon_count(features, t_idms, config):
        cc_main(features, t_idms=t_idms,config=config)
        return features
    
    @cache
    def _get_feature_carbon_labeling(features):
        return get_feature_carbon_labeling(features)
    
    @cache
    def _main_data_analysis(features, ident, analysis, sample_order, res_path):
        return main_data_analysis(features, ident, analysis, sample_order, res_path)
    
    @cache
    def _result_table(feature_labeling, summary_dic, config, result_path):
        return build_result_table(feature_labeling, summary_dic, config)
    
    def execute_workflow(config):
        t_idms=None
        # extract parameters from config
        fe=config['feature_extraction']
        group=fe['feature_extraction']
        ident=config['identification']
        analysis=config['data_analysis']
        align=config['feature_extraction']['alignment']
        data=config['project_data']        
        sample_order=config['project_data']['sample_order']
        project_path=config['project_path']
        res_path=config['project_folders']['results_directory']
        #process samples
        calib_table=build_calibration_table(config)
        peakmaps = load_peakmaps(config)
        ppms=_process_peakmaps(peakmaps, fe, calib_table)
        tables=_peakmaps2feature_tables(ppms, config)
        if data.get('internal_standard'):
            pm_idms= load_int_std(config)
            ppm_idms=_process_peakmaps([pm_idms], fe, calib_table)
            t_idms=_peakmap2feature_tables(ppm_idms[0], fe['ff_metabo'])
            tables.append(t_idms)
        # to obtain assistent rt times for samples and internal standard
        # int_std is appended to tables_list prior to alignment
        aligned_tables=_align_tables(tables, align, project_path, calib_table)
        # internal_standard is separated again after alignment
        if data.get('internal_standard'):
            t_idms=aligned_tables[-1]
            aligned_tables=aligned_tables[:-1]
        features=_regroup_and_cluster_features(aligned_tables, fe)
        sample_features=_extract_global_features(features, group, sample_order)
        sample_features=_carbon_count(sample_features, t_idms, ident)
        feature_labeling=_get_feature_carbon_labeling(sample_features)
        summary_dic=_main_data_analysis(feature_labeling, ident, analysis, sample_order, res_path) 
        result = build_result_table(feature_labeling, summary_dic, data, res_path)
        print config['project_data']['result']
        return result, config
    result=execute_workflow(config)
    return result
