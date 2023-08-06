# -*- coding: utf-8 -*-
"""
Created on Fri Apr 04 10:53:06 2014

@author: pkiefer
"""
import os
import helper_funs as helper

here = os.path.dirname(os.path.abspath(__file__))

def default_peak_extraction_alignment_config():
    MMU=0.001
    default=dict()
    default['ff_metabo']=dict(common_noise_threshold_int=1000.0,
                common_chrom_peak_snr=3.0,
                common_chrom_fwhm=25.0,
                mtd_mass_error_ppm=15.0,
                mtd_reestimate_mt_sd='true',
                mtd_trace_termination_criterion='outlier',
                mtd_trace_termination_outliers=5,                
                mtd_min_sample_rate=0.5,                
                mtd_min_trace_length=3.0,
                mtd_max_trace_length=350.0,
                epdet_width_filtering='off',
                epdet_min_fwhm=3.0,
                epdet_max_fwhm=60.0,
                epdet_masstrace_snr_filtering='false',
                ffm_local_rt_range=10.0,
                ffm_local_mz_range=10.0,
                ffm_charge_lower_bound=0, # peak_grouping is switched off
                ffm_charge_upper_bound=0,  # peak_grouping is switched off
                ffm_report_summed_ints='false',
                ffm_disable_isotope_filtering='true',
                ffm_use_smoothed_intensities='true')
    default['peakmap_processing']={'remove_shoulder':True,
                                'ignore_blanks':True}
    default['alignment']={'mz_alignment': True,
                            'rt_alignment': True,
                            'pair':0.01, 
                             'mz_diff':0.005, 
                             'rt_diff':100,
                             'ref': None,
                             'path': None,
                             'default_mass_calib': True, 
                               'mz_calib_table': _default_mass_calibration_table(), 
                               'cal_path':here, 
                               'mztol': 10*MMU, 
                               'minR2': 0.6, 
                               'maxTol':0.001,
                               'minPoints':5, 
                               "interactive": False}   
    default['feature_extraction']={"rt_tol":25, 
                                   "isol_width": 3*MMU, 
                                   "delta_mz_tolerance": 0.8*MMU,
                                   'suitability_test': False,
                                   "rel_min_area": 0.01,
                                   'z_range':(1,3),
                                   'max_c_gap':10}
    return default

def _default_mass_calibration_table(empty=False):
    default={'adduct': ('M-H', 'M-H', 'M-H', 'M-H', 'M-H', 'M-H', 'M-H', 'M-H', 'M-2H', 'M-H',
            'M-3H', 'M-2H', 'M-3H', 'M-2H', 'M-3H', 'M-2H', 'M-3H','M-2H'),
            'id': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18),
 'instrument_method': ('400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method',
                   '400 ul/min_105x0.1mm 3um porsize, Dr. Maisch C18 reprosil gold_IPRP_method'),
 'layout': [('id', "<type 'int'>", '%d'),
            ('name', "<type 'str'>", '%s'),
            ('mf', "<type 'str'>", '%s'),
            ('mass', "<type 'float'>", '%.5f'),
            ('adduct', "<type 'str'>", '%s'),
            ('mass_shift', "<type 'float'>", '%.5f'),
            ('z', "<type 'int'>", '%d'),
            ('polarity', "<type 'str'>", '%s'),
            ('mz_hypot', "<type 'float'>", '%.5f'),
            ('rtmin', "<type 'float'>", "'%.2fm' % (o/60.0)"),
            ('rtmax', "<type 'float'>", "'%.2fm' % (o/60.0)"),
            ('instrument_method', "<type 'str'>", '%s')],
 'mass': (151.9876378395, 153.98468774949998, 266.1551815594, 515.2916761655, 
          472.95973490470004, 523.2576899103001, 552.9260664266001, 632.8923979485, 
          632.8923979485, 848.3300665312, 848.3300665312, 848.3300665312, 905.1024571241, 
          905.1024571241, 949.0519415440999, 949.0519415440999, 1012.398541914, 1012.398541914),
 'mass_shift': (-1.007276466812, -1.007276466812, -1.007276466812, -1.007276466812, -1.007276466812,
                -1.007276466812, -1.007276466812, -1.007276466812, -2.014552933624, -1.007276466812,
                -3.0218294004360002, -2.014552933624, -3.0218294004360002, -2.014552933624,
                -3.0218294004360002, -2.014552933624, -3.0218294004360002, -2.014552933624),
 'mf': ('C4H5O4Cl', 'C4H5O4[37]Cl', 'C12H26O4S', 'C26H45NO7S', 'C10H13N5O7PI', 'C23H37N7O5S',
        'C10H14N5O10P2I', 'C10H15N5O13P3I', 'C10H15N5O13P3I', 'C35H48N10O15', 'C35H48N10O15',
        'C35H48N10O15', 'C28H39ClN7O17P3S', 'C28H39ClN7O17P3S', 'C28H39N7O17P3SBr',
        'C28H39N7O17P3SBr', 'C41H60N10O20', 'C41H60N10O20'),
 'mz_hypot': (150.980361372688, 152.977411282688, 265.14790509258796, 514.284399698688,
              471.952458437888, 522.2504134434881, 551.9187899597881, 631.8851214816881,
              315.438922507438, 847.3227900643881, 281.76941237692137, 423.157756798788,
              300.69354257455467, 451.543952095238, 315.3433707145546, 473.51869430523794,
              336.458904171188, 505.191994490188),
 'name': ('Chloro-succinate', 'Chloro-succinate_Cl37', 'SDS',
          'Taurocholate', 'Iodo-AMP', 'MRFA', 'Iodo-ADP', 'Iodo-ATP', 'Iodo-ATP',
          'DSIP', 'DSIP', 'DSIP',
          'Chloro-benzoyl-coA', 'Chloro-benzoyl-coA', 'Bromo-benzoyl-coA', 'Bromo-benzoyl-coA',
          'FLAG', 'FLAG'),
 'polarity': ('-',)*18,
 'rtmax': (900.0, 900.0, 1986.0, 1800.0, 960.0, 1140.0, 1140.0, 1140.0, 1140.0,
           1152.0, 1152.0, 1152.0,
           1390.8, 1390.8,
           1401.6, 1401.6,
           1080.0, 1080.0),
 'rtmin': (720.0, 720.0, 1686.0, 1500.0, 720.0, 900.0, 840.0, 840.0, 840.0,
           852.0, 852.0, 852.0, 1151.4, 1151.4, 1161.0, 1161.0, 780.0, 780.0),
 'z': (1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 3, 2, 3, 2, 3, 2, 3, 2)}
        
    if not empty:
        return default
    else:
        return _build_empty_ms_calib_t(default)
        
def _build_empty_ms_calib_t(default):
    d=default
    d=helper.dict_to_table(d)
    raw=[None for i in range(len(d.getColNames()))]
    empty=d.buildEmptyClone()
    empty.addRow(raw)
    print len(empty)
    return empty


def default_identification():
    default=dict()
    default['instr_linear_error']=0.03
    default['rttol']=25
    default['isol_width']=0.003
    default['idms_sample']=True
    default['c_source_labeling']=0.99
    default['max_c_istd']=40
    default['data_base']='kegg'
    return default

def default_data_analysis():
    default=dict()
    default['min_labeling']=0.8 # min number of incorporated labeled atoms
    default['feature_frequency']=0.8 # number of samples of samples in which feature occurs versus 
                                     # total sample number
    default['max_nrmse']=0.25 # maximual normalizesd root-mean-square deviation accepted for 
                                # labeling profile fitting
    default['clustering_cut_off_threshold']=0.5 #to perform hierarchical clustering using the single linkage algorithm,
                                                #and to form flat clusters using the inconsistency method with `t` as the
                                                #cut-off threshold.
    return default

def initialize_project_dic():
    project_dic=dict()
    project_dic['peakmaps']=None
    project_dic['sample_order']=None
    project_dic['internal_standard']=None
    project_dic['result']=None
    return project_dic


def default_suitability_test(default):
    suit={}
    calib=_default_mass_calibration_table()
    t=helper.dict_to_table(calib)
    test_table=t.extractColumns('name', 'mf', 'rtmin', 'rtmax', 'adduct', 'mass_shift', 'z',
                                'polarity')
    test_table.renameColumns(**{'adduct':'adduct_name'})
    helper.add_mf_ion(test_table)
    test_table.addEnumeration()
    suit['Orbitrap_instrument']=True
    suit['test_table']=helper.table_to_dict(test_table)
    suit['ref_R']=(60000,400)
    default['suitability_test']=suit
    
    
def get_default_config():
    """ returns dictionary with default DynaMet parameters
    """
    default = dict()
    default['feature_extraction'] = default_peak_extraction_alignment_config()
    default['identification'] = default_identification()
    default['data_analysis'] = default_data_analysis()
    default['project_folders'] = None
    default['project_data'] = initialize_project_dic()
    default_suitability_test(default)
    return default


        
def find_delta_glu(t):
    t1=t.copy()
    delta_glu=129.01
    resulting=t.join(t1, (t.mz*t.z-t1.mz*t1.z).approxEqual(delta_glu, 0.005))
    return resulting
        
