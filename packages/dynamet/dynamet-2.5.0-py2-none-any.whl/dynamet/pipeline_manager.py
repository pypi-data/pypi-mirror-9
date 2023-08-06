# -*- coding: utf-8 -*-
"""
Created on Thu Apr 03 14:57:58 2014

@author: pkiefer
"""
from config_manager import setup_project_data
import glob
import os
import emzed
from run_pipeline import setup_wf
from config_manager import manage_config

##############################################################################################

def run_analysis(config, mode=0):
   setup_project_data(config) 
   result, config=setup_wf(config)
   emzed.gui.showInformation('FINISHED')
   manage_config(None, config=config)
   return result, config


def inspect_result(config):
    target=config['project_data']['result']
    result = None
    if target:
        choice=['current', 'all']
        choose=emzed.gui.DialogBuilder('inspect results')\
        .addMultipleChoice('choose:', choice, default = [0] )\
        .show()
        if not sum(choose):
            result=target
        
    if not result:
        result_path=config['project_folders']['results_directory']
        name='*.table'
        target=os.path.join(result_path, name)
        files=glob.glob(target)
        files=match_result_files(files)
        if not len(files):
            emzed.gui.showWarning('results are missing! Please first run analysis!')
        else:
            files.sort(reverse=True)
            names=[os.path.basename(f) for f in files]
            i=emzed.gui.DialogBuilder('choose_result_table')\
            .addChoice('select', names)\
            .show()
            result=files[i]
    if result:
        emzed.gui.inspect(emzed.io.loadTable(result))
    

def match_result_files(files):
    import re    
    pattern='[0-9]{8}_[0-9]{2}h[0-9]{2}m[0-9]{2}s_dynamet'
    return [f for f in files if re.match(pattern, os.path.basename(f))]
        

def reset_project(config, basic=True, int_results=True):
    for key in config['project_data'].keys():
        config['project_data'][key]=None
    manage_config(None, config=config)
    emzed.gui.showInformation('Done')
    return config
    
    
