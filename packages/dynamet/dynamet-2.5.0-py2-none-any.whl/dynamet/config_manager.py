# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 14:30:44 2014

@author: pkiefer
"""
import os
from project_creator_dli import project_structure_manager
from objects_check import monotonic
from idms_metabolite_identifyer import get_external_data_base
import glob
import pipeline_configs
import emzed
import helper_funs as helper
import objects_check as check
import numpy as np
####################################################################

# SAVE ans INITIALIZE CONFIG, SYNCHRONIZE PARAMETERS
#################################################################
def manage_config(project_path, config=None, name=None):
        if not config:
            assert os.path.isdir(project_path)
            config=_check_for_config(project_path)          
            config['project_folders']=project_structure_manager(project_path)
            config['project_path']=project_path
        else:
            if not config['project_folders']:             
                config['project_folders']=project_structure_manager(project_path)
            if not config['project_path']:
                assert os.path.isdir(project_path)
                config['project_path']=project_path
        if not name:
            name='dynamet_config'
        _update_config_dicts(config)
        config_path=config['project_folders']['toolbox_directory']
        print config_path
        assert os.path.isdir(config_path)
        helper.save_dict(config, name, config_path, overwrite=True)
        return config    


def _update_config_dicts(config):
    """ Values occuring in more than processes which use different config dictionarys
        are changed in the gui only once are updated in all other dictionarys. Might be
        replaced in the future by a flattened dictioary structure...
    """
    fe='feature_extraction'
    config['identification']['isol_width']=config[fe][fe]['isol_width']
    config['identification']['rttol']=config[fe][fe]['rt_tol']
    config['identification']['delta_mz_tol']=config[fe][fe]['delta_mz_tolerance']
    config['suitability_test']['isol_width']=config[fe][fe]['isol_width']

def _check_for_config(project_path):
    path=get_config_path(project_path)
    base_name='*.json'
    target=os.path.join(path,base_name)
    targets=glob.glob(target)
    if not len(targets):
        config=pipeline_configs.get_default_config()
    elif len(targets)==1:
        config=helper.load_dic(path=targets[0])
    else:
        choose=[os.path.basename(target) for target in targets]
        choose.append('load_default')
        choice=emzed.gui.DialogBuilder('load pipeline_config')\
        .addChoice('choose_config', choose)\
        .show()
        print choice
        print len(targets)
        if choice==len(targets):
            config=pipeline_configs.get_default_config()
        else:
            config=helper.load_dic(path=targets[choice])
    # add toolbox path
    config['path']=path
    return config
    
    
def get_config_path(path):
    project_folders=project_structure_manager(path)
    return project_folders['toolbox_directory']


def _save_config(config, path):
    """
    """
    label=helper.time_label()
    name=label+'pipeline_parameters'
    helper.save_dict(config, name, path)

#################################################################################################

# ADAPT AND MODIFY CONFIG PARAMETERS BY USER
#################################################################################################
def adapt_feature_detection_config(config):
    dic=config['feature_extraction']
    folders=config['project_folders']
    pm_path= folders['peakmaps_directory']
    toolbox_path=folders['toolbox_directory']
    process, align, ff, group =emzed.gui.DialogBuilder('MODIFY FEATURE DETECTION CONFIG')\
    .addMultipleChoice('peakmap_processing', ['ignore_blanks', 'orbitrap_data'], default=[0,1],\
    help='samples with `_blank_` or `_Blank_` in filename are ignored.\n `Orbitrap data` option '\
    'allows removing shoulder artefact peaks around intense peaks')\
    .addMultipleChoice('alignment', ['retention time', 'mass'], default=[0,1])\
    .addMultipleChoice('peak_detection', ['default', 'advanced'], default=[0],
                       help='if both fields are chosen advanced settings will be selected')\
    .addMultipleChoice('feature_grouping', ['adapt'], default=[0])\
    .show()
    print process, align, ff, group
    print''
    _adapt_peakmap_processing_config(dic, process)
    _adapt_alignment_config(dic, pm_path, toolbox_path, align)
    _adapt_ff_metabo_config(dic, ff)
    _adapt_reference_table_settings(dic, group)
    manage_config(None, config=config)




def _adapt_ff_metabo_config(settings, advanced=[0]):
    
    if len(advanced):
        advanced=sum(advanced)
        width_filter=["off", "auto", "fixed"]    
        # sum==0: advanced off, sum==1: advanced  == on, since multiple choice dialog
        dic=settings['ff_metabo']
        criterion=['outlier', 'sample_rate']
        names=['common_noise_threshold_int', 'common_chrom_peak_snr', 'common_chrom_fwhm',
               'mtd_mass_error_ppm', 'mtd_reestimate_mt_sd', 'mtd_trace_termination_criterion',
               'mtd_trace_termination_outliers', 'mtd_min_sample_rate', 'mtd_min_trace_length',
               'mtd_max_trace_length', 'epdet_width_filtering', 'epdet_min_fwhm','epdet_max_fwhm',
               'epdet_masstrace_snr_filtering']
        # HELPER Funs
        # openMS uses strg instead of  boolean value:
        def bools_fun(key):
            dic={'true': True, 'false': False}
            return dic[key] if dic.has_key(key) else False
        # inverse fun to bools_fun
        def boolToStr(value):
            return "true" if value else "false"
            
        def get_index(v, liste):
            if v in range(len(liste)):
                return liste.index(v)
            else:
                return 0
        # GUI        
        if advanced:
            params=emzed.gui.DialogBuilder("Configure Peak Detection")\
            .addFloat(names[0], default=dic[names[0]], min=1.0,
                      help="intensity threshold below which peaks are regarded"\
                      " as noise")\
            .addFloat(names[1], default=dic[names[1]], help="minimum signal-"\
                        "to-noise a mass trace should have")\
            .addFloat(names[2], default=dic[names[2]], min=1.0, max=120.0,
                      help="typical peak width (full width at half maximum)")\
            .addFloat(names[3], default=dic[names[3]], help="allowed mass deviation")\
            .addBool(names[4], default=bools_fun(dic[names[4]]), help="enables dynamic re-"\
                    "estimatation of m/z variance during mass trace collection state")\
            .addChoice(names[5], criterion ,default=get_index(dic[names[5]], criterion), 
                       help='Termination criterion for the extension of mass traces.\n In `outlier` mode,'\
                       'trace extension cancels if a predifined number of consecutive outliers are found'\
                       '(see trace_termination_outliers parameter).\n In `sample_rate` mode, trace '\
                       'extension in both direction stops if ratio of found peaks versus visited spectra'
                       'falls below `min_sample_rate` threshold')\
            .addInt(names[6], default=dic[names[6]], help='mass trace extension in one direction'\
                    'cancels if set value of consecutive spectra without detected peaks is reached')\
            .addFloat(names[7], default=dic[names[7]], help='minimum fraction of scans along the mass trace'\
                    'that must contain a peak')\
            .addFloat(names[8], default=dic[names[8]], min=1.0, help="minimum expected"\
                        " length of a mass trace (in seconds)")\
            .addFloat(names[9], default=dic[names[9]], min=1.0, help="maximum expected"\
                        " length of a mass trace (in seconds)")\
            .addChoice(names[10], width_filter ,default=get_index(dic[names[10]], width_filter),
                       help="enable filtering of"\
                    " unlikely peaks width.\n The fixed setting filters out mass traces"\
                    " outside the\n [min_fwhm, max_fwhm] interval (please set parameters"\
                    " accordingly!).\n The auto setting filters with the 5% and 95%"\
                    "quantiles of the peak width distribution.")\
            .addFloat(names[11], default=dic[names[11]], min=1.0, help="minimum full-width"\
                        "-at-half-maximum of chromatographic peak (in seconds).\n"\
                        "Ignored if parameter epd_width_filtering is off or auto.")\
            .addFloat(names[12], default=dic[names[12]], min=2.0, help="maximum full-width"\
                        "-at-half-maximum of chromatographic peak (in seconds).\n"\
                        "Ignored if parameter epd_width_filtering is off or auto.")\
            .addBool(names[13], default=bools_fun(dic[names[13]]), help="apply post"\
                    "-filtering by signal-to-noise ratio after smoothing")\
            .show()
            # replace changed parameters    
            for i,value in enumerate(params):
                if i in [4, 13]:
                    dic[names[i]]=boolToStr(value)
                elif i == 5:
                    dic[names[i]]=criterion[value]
                elif i == 10:
                    dic[names[i]]=width_filter[value]
                else:
                    if i<len(params)-1:
                        dic[names[i]]=value
        else:
            #debug
            print 'hier', names[10], dic[names[10]]
            switch=["off", "on"]
            params=emzed.gui.DialogBuilder("Configure Peak Detection")\
            .addFloat(names[0], default=dic[names[0]], min=1.0,
                      help="intensity threshold below which peaks are regarded"\
                      " as noise")\
            .addFloat(names[1], default=dic[names[1]], help="minimum signal-"\
                        "to-noise a mass trace should have")\
            .addFloat(names[2], default=dic[names[2]], min=1.0, max=120.0,
                      help="typical peak width (full width at half maximum)")\
            .addFloat(names[3], default=dic[names[3]], help="allowed mass deviation")\
            .addBool(names[4], default=bools_fun(dic[names[4]]), help="enables dynamic re-"\
                    "estimatation of m/z variance during mass trace collection state")\
            .addChoice(names[10], switch ,default=get_index(dic[names[10]], 
                       width_filter),   help="enable filtering of"\
                    " unlikely peaks width.\n The auto setting filters with the 5% and 95%"\
                    "quantiles of the peak width distribution.")\
            .show()
            # replace changed parameters 
            for i,j in enumerate([0, 1, 2, 3, 4, 10]):
                if j==4:
                    dic[names[j]] = boolToStr(params[i])
                    print boolToStr(params[i])
                elif j==10:
                    dic[names[j]] = width_filter[params[i]]
                else:
                     if i<len(params)-1:
                        dic[names[j]]=params[i]

########################################################################



def _adapt_reference_table_settings(settings, run=[0]):
    dic=settings['feature_extraction']
    keys=['isol_width', 'z_range', 'max_c_gap', 'rel_min_area']
    z_range = range(5)
    z_range_ = [str(i) for i in z_range]
    if 0 in run: # multiple choice selection
        params=emzed.gui.DialogBuilder("Feature Grouping")\
        .addFloat('isolation width', default=dic[keys[0]], help='Maximal mz difference'\
        ' between mass traces (value in U) of different samples tolerated as same mz value')\
        .addChoice('charge_lower_bond', z_range_, default=dic[keys[1]][0], help = 'lowest charge '\
                                                                        'state z to consider')\
        .addChoice('charge_upper_bond', z_range_, default=dic[keys[1]][1], help = 'highest charge '\
                                                                        'state z to consider')\
        .addInt('max_c_gap', default=dic[keys[2]], help =' maximal allowed carbon gap width n for '\
                'n in n*(13C- 12C) within feature isotopic pattern.')\
        .addFloat('relative minimal peak area', default=dic[keys[3]], help='lowest peak area'\
                    ' relative to the base peak area accepted.')\
        .show()
        print params
        z_range=[params[1], params[2]]
        dic['z_range']=z_range
        for i, value in enumerate(params):
            if i ==0:
                dic[keys[i]]=params[i]        
            if i >2:
                dic[keys[i-1]]=params[i]   


def _adapt_peakmap_processing_config(config, modify=[0,1]):
    dic=config['peakmap_processing']
    keys=['ignore_blanks', 'remove_shoulder']
    helper.dic_has_keys(dic, keys)
    for i,key in enumerate(keys):
        dic[key] = True if i in modify else False
    config['peakmap_processing']=dic
    return config


def _adapt_alignment_config(config, pm_path, toolbox_path, choices=[0,1]):
    dic=config['alignment']
    keys0=['rt_alignment','pair', 'mz_diff', 'rt_diff']
    keys1=['mz_alignment', 'mz_cal_table','mztol', 'minR2', 'minPoints', 'maxTol', "interactive"]
    if 0  in choices:        
        params=_gui_rt_alignment(dic, keys0)
        for i,key in enumerate(keys0):
           dic[key]=params[i]
    if 1 in choices:
        params=_gui_mz_alignment(dic, keys1)    
        for i,key in enumerate(keys1):
            if i !=1:
                dic[key]=params[i]
        #'paramerter[1] is mass calibration table and value is processed separately:'
        modified=modify_mass_calibration_table(dic, params[1], pm_path, toolbox_path)
        if modified:
            dic['mz_cal_table']=modified

def _gui_rt_alignment(dic, keys):
    align = ['on', 'off']
    default=0 if dic[keys[0]] else 1
    params=emzed.gui.DialogBuilder('Modify retention time alignemnt (OpenMS))')\
        .addChoice('rt_alignment', align, default=default)\
        .addFloat('maxMzDifferencePairfinder', dic[keys[1]], help=' max allowed difference in mz'\
        ' values for pair finding')\
        .addFloat(keys[2], dic[keys[2]], help='max allowed difference in mz'\
        ' values for super_imposer')\
        .addFloat(keys[3], dic[keys[3]], help='max allowed difference in rt values for'\
                                          ' searching matching features.')\
        .show()
    params=list(params)
    params[0] = True if params[0] == 0 else False
    return params


def _gui_mz_alignment(dic, keys):
    align = ['on', 'off']
    default=0 if dic[keys[0]] else 1
    choice=['default', 'load different', 'inspect / modify', 'build new']
    params=emzed.gui.DialogBuilder('Modify mass calibration')\
    .addChoice(keys[0], align, default=default)\
    .addChoice('process calibration table', choice, default=0)\
    .addFloat(keys[2], default=dic[keys[2]], help='maximal tolerated mass'\
                                                 ' difference to match a peak with calibrant.')\
    .addFloat(keys[3], default=dic[keys[3]], help='Stop criterion when removing outlier points')\
    .addInt(keys[4], default=dic[keys[4]], help='Minimal number of points for calibration curve fitting')\
    .addFloat(keys[5], default=dic[keys[5]], help=' Maximal tolerated mass deviation after'\
            'calibration. Stop criterion when removing outlier points.')\
            .addBool(keys[6], default=dic[keys[6]], help='if True manual inspection and data point removal'\
    'is enabled. For automatic data processing this is not recommended!')\
    .show()
    params=list(params)
    params[0] = True if params[0] == 0 else False
    return params


###################################################################################################
def modify_mass_calibration_table(config, choice, pm_path, toolbox_path):
    print 'choice', choice
    if choice == 1:
        path=_create_dummy_table(toolbox_path)
        _, path=emzed.gui.DialogBuilder('choose_mass_calibration_table')\
        .addButton('help', _help)\
        .addFileOpen('open mass calibration table', default=path,
                     basedir=toolbox_path, formats=['table'])\
        .show()
        print 'loading calibration table...'
        t=emzed.io.loadTable(path)
        _check_calib_table_format(t)
        t=_inspection(pm_path, t, config['mztol'])
        config['mz_calib_table']=helper.table_to_dict(t)
        print 'Done.'
    if choice == 2:
        t=helper.dict_to_table(config['mz_calib_table'])
        t=_inspection(pm_path,t, config['mztol'])
        config['mz_calib_table']=helper.table_to_dict(t)
        print 'Done.'
    if choice == 3:
        t=pipeline_configs._default_mass_calibration_table(empty=True)
        t=_inspection(pm_path, t, config['mztol'])
        config['mz_calib_table']=helper.table_to_dict(t)
        print 'Done.'


def _create_dummy_table(path):
    t=pipeline_configs._default_mass_calibration_table(empty=True)
    target=os.path.join(path, 'mass_calib_table_dummy.table')
    if not os.path.exists(target):
        emzed.io.storeTable(t, target)  
    return target
        


def _check_calib_table_format(t):
    required=['id', 'mf', 'adduct', 'mass_shift', 'z', 'polarity', 'mz_hypot', 'rtmin', 'rtmax']
    check.table_has_colnames(required,t)


def _inspection(path, t, mztol=10*emzed.MMU):
    if t.mz_hypot.countNone() >0:
        text= 'Table contains None values. Please enter / complete calibrant data. '\
        'You can clone lines by pressing the'\
        ' button at the beginning of each line with the right mouse.'\
        ' Important: mz_hypot, rtmin and rtmax'\
        ' must not be None!'
        emzed.gui.showInformation(text)
        emzed.gui.inspect(t)
    target=emzed.gui.DialogBuilder('Choose peakmap to adapt rtmin and rtmax')\
    .addFileOpen('open peakmap', basedir=path, formats=['mzXML', 'mzML'])\
    .show()
    pm=emzed.io.loadPeakMap(target)
    t.addColumn('peakmap', pm)
    t.addColumn('mzmin', t.mz_hypot-mztol)
    t.addColumn('mzmax', t.mz_hypot+mztol)
    t=emzed.utils.integrate(t, 'no_integration')
    emzed.gui.showInformation('To adapt retention time windows move '\
        'rt window bounderies with the mouse and then press Table `integrate` button.')    
    emzed.gui.inspect(t)
    t.dropColumns('peakmap', 'params', 'area', 'rmse', 'mzmin', 'mzmax')
    return t


def _help(data):
    emzed.gui.showInformation('Select a mass calibraton table. Mandatory table columns'\
        ' ``mz_hypot`` for the mz value calculated from the mass of the isotope,'\
        ' ``rtmin``, ``rtmax`` for the retention time window where the peak'\
    ' is expected to elute from the column in order to restrict the match of the table against'\
    ' the  ``mz_reference_table`.')\

###################################################################################################    
def adapt_identification_config(config):
    path=config['project_folders']['toolbox_directory']
    dic=config['identification']
    keys=['instr_linear_error', 'idms_sample', 'c_source_labeling', 'max_c_istd',
          'data_base']
    helper.dic_has_keys(dic, keys)
    choose=['kegg', 'pubchem', 'hmdb', 'other']
    def get_index(v, liste):
        return liste.index(v)
    params=emzed.gui.DialogBuilder('Modify identification parameters')\
    .addFloat(keys[0], default=dic[keys[0]], help='absolute instrumental error on area measurement'\
    'e.g. orbitrap classic 0.03 (3 %)')\
    .addBool(keys[1], default=dic[keys[1]], help='isotope dilution sample, a sample composed out'\
    'of 1 : 1 mixture of a cell extract cultivated on [U-13C] labeled carbon source'\
    'for at least 5 generationa (all metabolites are maximal labeled) and a natural labeled sample,'\
    ' idealy orginating from the same strain or cell line.')\
    .addFloat(keys[2], default=dic[keys[2]], help='enter value for labeled fraction of applied'\
            ' substrate used for dynamic labeling experiment, e.g. 0.99.')\
    .addInt(keys[3], default = dic[keys[3]], help='Value corresponds to the maximum number of'\
        'carbon atoms for metabolites of interests.')\
    .addChoice(keys[4], choose, default=get_index(dic[keys[4]],choose), 
               help='Choose emzed integrated data base or use'\
    'your own data base. Assure that your db it is compatible with pipeline.')\
    .show()
    for i,key in enumerate(keys):
        if i==4:
            dic['data_base'] = choose[params[i]]
            if dic['data_base']=='other':
                dic['data_base']=get_external_data_base(path)
        else:
            dic[key]=params[i]
    config['identification']=dic
    manage_config(None, config=config)
    
    
    
###################################################################################################
def adapt_data_analysis_config(config):
    dic=config['data_analysis']
    keys=['min_labeling', 'feature_frequency', 'max_nrmse']
    helper.dic_has_keys(dic, keys)
    
    params=emzed.gui.DialogBuilder('Modify data analysis parameters')\
    .addFloat(keys[0], default=dic[keys[0]], help='minimal labeled carbon fraction of feature '\
                                                'observed in at least one sample')\
    .addFloat(keys[1], default=dic[keys[1]], help='frequency of feature occurance'\
                                    ' in sample set')\
    .addFloat(keys[2], default=dic[keys[2]], help='maximal normalized root-mean-square deviation'\
                                    'accepted for labeling profile fitting')\
    .show()
    for i,key in enumerate(keys):
        dic[key]=params[i]
    config['data_analysis']=dic
    manage_config(None, config=config)


###################################################################################################
def adapt_suitability_test_config(config):
    dic=config['suitability_test']
    keys=['Orbitrap_instrument','ref_R']
    choice=['400','200']
    helper.dic_has_keys(dic, keys)
    params=emzed.gui.DialogBuilder('Modify instrument specification for suitability test')\
    .addBool(keys[0], default=dic[keys[0]], help='Applied MS instrument is of type Orbitrap')\
    .addInt('Unit Mass Resolution R', default=dic[keys[1]][0], help='Resolution in m/delta_m')\
    .addChoice('R at mz',choice,default=0, help='parameter only for Orbitrap instruments: '\
    'QExactive models: 200, all others 400')\
    .show()
    if not params[0]:
        params[-1]=0
    dic[keys[0]]=params[0]
    dic[keys[-1]]=(params[1], int(choice[params[2]]))
    config['suitability_test']=dic
    manage_config(None, config=config)
    

##################################################################################################
# SELECT PROJECT DATA
#################################################################################################

def setup_project_data(config):
    has_int_std=config['identification']['idms_sample']
    if not config['project_data']['peakmaps']:
        add_pm_pathes_to_config(config)
        add_sample_order_to_config(config)
    if has_int_std and not config ['project_data']['internal_standard']:
        add_int_std_to_config(config)
    manage_config(None, config=config)
  

def add_pm_pathes_to_config(config):
    pm_path=config['project_folders']['peakmaps_directory']
    ignore_blanks=config['feature_extraction']['peakmap_processing']['ignore_blanks']
    names=[]
    default=['*.mzXML', '*mzMl']
    for ending in default:
        target=os.path.join(pm_path, ending)
        names.extend(glob.glob(target))
    if ignore_blanks:
       names=filter_blanks(names) 
    names.sort()
    depict=[os.path.basename(n) for n in names]
    default=range(len(names))
    verticals=int(np.ceil(len(names)/10.0))
    select=emzed.gui.DialogBuilder('Select Dynamic Labeling Samples')\
    .addMultipleChoice('choose', depict, default=default, vertical=verticals)\
    .show()
    config['project_data']['peakmaps']=[names[i] for i in select]


def filter_blanks(filenames, labels=['_blank_', '_Blank_', '_BLANK_', '_blank.', 
                                     '_Blank.', '_BLANK.']):
    assert isinstance(filenames, list), 'FILENAMES ARE NOT IN A LIST'
    assert all([isinstance(n, str) for n in filenames]), 'List of filenames contains'\
                                                        ' at least 1 non-string object'
    labels=labels
    def fun(v, labels=labels):
        check=[v.find(label)<0 for label in labels]
        if all(check):
            return True
    return [n for n in filenames if fun(n)]
    

def add_sample_order_to_config(config):
    dic=config['project_data']
    dic['sample_order']=define_sample_order(dic['peakmaps'])


def define_sample_order(filenames):
    """
    """
    names=[os.path.basename(name) for name in filenames]
    names.sort()
    emzed.gui.showInformation("Please enter sample order (0-n) and \ntime"
    " points of labeling incorporation")
    t=emzed.utils.toTable("sample_names", names)
    t.addColumn("sample_order", range(len(names)))
    t.addColumn("time", 0.0, format_="%.1fs")
    t.title="sample order"
    emzed.gui.inspect(t)
    try:
        monotonic(t, 'sample_order', 'time', ascending=True)
    except:
        emzed.gui.showWarning('sample order and time are not monontonically ascending'\
        'Values will be resetted')
        define_sample_order(filenames)
    return helper.table_to_dict(t)


def add_int_std_to_config(config):
    pm_path=config['project_folders']['peakmaps_directory']
    ignore_blanks=config['feature_extraction']['peakmap_processing']['ignore_blanks']
    names=[]
    default=['*.mzXML', '*mzMl']
    for ending in default:
        target=os.path.join(pm_path, ending)
        names.extend(glob.glob(target))
    if ignore_blanks:
       names=filter_blanks(names) 
    names.sort()
    depict=[os.path.basename(n) for n in names]
    pos=emzed.gui.DialogBuilder('Select uniformly labeled samples')\
        .addChoice('choose U13C sample', depict)\
        .show()
    config['project_data']['internal_standard']=names[pos]

