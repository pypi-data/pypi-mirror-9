# -*- coding: utf-8 -*-
"""
Created on Thu Apr 03 14:22:10 2014

@author: pkiefer
"""
import emzed.gui as gui
#import helper_funs as helper
import config_manager
import pipeline_manager
import suitability_test as suitable
import os
import webbrowser
here = os.path.dirname(os.path.abspath(__file__))

class PipelineGui(gui.WorkflowFrontend):
    """
    """
    
    project_path=gui.DirectoryItem('project path', default=r'Z:\pkiefer\orbitrap_data\temp_2', 
                                   help='enter main project folder path. '\
                                'If a new project is initialized enter path with LC-MS data.'\
                                'A new project structure will be built automaticaly')
    docu_=gui.RunJobButton('Documentation', method_name='get_documentation')
    config=gui.RunJobButton('change_pipeline_config', method_name='change_config_settings')
    run_pipeline=gui.RunJobButton('run analysis', method_name='start_analysis')
    inspect_result=gui.RunJobButton('inspect result', method_name='inspect')
    suitability_test=gui.RunJobButton('suitability_test', method_name='suitable')
    reset_pipeline=gui.RunJobButton('reset data analysis', method_name='reset')
    
    
    def get_documentation(self):
        path=os.path.join(here, r'docs\20141030DYNAMET DOCUMENTATION.htm')
        webbrowser.open(path)

    def change_config_settings(self):
        print self.project_path
        self.config=config_manager.manage_config(self.project_path, config=self.config)
        gui.DialogBuilder('change pipeline configuration settings')\
        .addButton('feature_detection', self.modify_feature_detection, 
                   help='general parameters for feature detection and basic processing e.g. alignment')\
        .addButton('identification', self.modify_identification,
                   help='choose identification mode and data base')\
        .addButton('feature analyis', self.modify_data_analysis, 
                   help='configuration for feature selection')\
        .addButton('suitability test', self.modify_suitability,
                   help='change instrument parameters for test')\
        .show()
    
    def modify_feature_detection(self, data):
        config_manager.adapt_feature_detection_config(self.config)

    
    def modify_identification(self, data):
        print 'modify identification config...'
        config_manager.adapt_identification_config(self.config)

        
    def modify_data_analysis(self, data):
        print 'modify data analysis config...'
        config_manager.adapt_data_analysis_config(self.config)


    def modify_suitability(self, data):
        print 'adapt parameters for suitability test...'
        config_manager.adapt_suitability_test_config(self.config)
     
    def start_analysis(self):
        self.config=config_manager.manage_config(self.project_path)
        # load samples
        self.result, self.config=pipeline_manager.run_analysis(self.config)

        
    def inspect(self):
        if not self.config:
            self.config=config_manager.manage_config(self.project_path)
        pipeline_manager.inspect_result(self.config)


    def suitable(self):
        if not self.config:
            self.config=config_manager.manage_config(self.project_path)
        suitable.main_suitable(self.config)

    
    def reset(self):
        if not self.config:
            self.config=config_manager.manage_config(self.project_path)
        choose=gui.DialogBuilder('RESET PROJECT')\
        .addChoice('resetting data analyis?', ['yes', 'no'], default=0,
                  help='previous results will be kept')\
        .show()
        if choose==0:
            self.config=pipeline_manager.reset_project(self.config)
        
def run():
    PipelineGui().show()    
    
if __name__ == '__main__':
    run()