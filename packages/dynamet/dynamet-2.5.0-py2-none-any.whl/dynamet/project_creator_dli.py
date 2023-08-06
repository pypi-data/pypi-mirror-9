# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 11:35:10 2011

@author: pkiefer
"""
import emzed
import os
import shutil
import glob
here=os.path.dirname(os.path.abspath(__file__))

##############################################
# functions to create Dynamet project
#############################################


def _check_path(path, directories):
    """ checks whether given path for new project is conform with
        mandatory data structure.
    """
    expr=os.path.join
    types=[".dli_project"]
    fields=path.split(os.sep)
#    print fields
    for type_ in types:
        while len(fields):
            sub=os.sep.join(fields)+type_
            if os.path.exists(sub):
               emzed.gui.showWarning('Chosen Folder is part of an existing project %s!!'\
                             'PLEASE CHOOSE / CREATE AN OTHER FOLDER' %sub)
               return
            fields.pop()
    folderelements=os.listdir(path)
    print folderelements
    dirs=[ expr(path,elem) for elem in folderelements if os.path.isdir(expr(path, elem))]
    print dirs
    print len(dirs)
    default = directories.values()
    default.sort()
    dirs.sort()
    if (default == dirs) or len(dirs)==0:
        return True    
    emzed.gui.showWarning("CHOSEN FOLDER CONTAINS SUBFOLDERS "\
                        'IF YOU WANT TO CREATE A NEW PROJECT:'\
                        'PLEASE CHOOSE or CREATE AN OTHER FOLDER ELSEWHERE')
    return


def _get_project_directories(path):
    """
    """
    expr=os.path.join
    dirs={'raw_directory' : 'ACQUISITION_DATA',
     'instr_directory' : 'INSTRUMENT_DATA',
    'peakmaps_directory' : "PEAKMAPS",
    'cache_directory' : "CACHE",
    'results_directory' : "RESULTS",
    'toolbox_directory' : 'TOOLBOX'}

    for key in dirs.keys():
        dirs[key]=expr(path, dirs[key])
    return dirs


def create_project(path, type_=".dli_project", mode='scan'):
    """ creates folder tree for alignment tool. The tree is made for
        untargeted extraction from dynamics labeling experimnet data
    """
    print 'Creating dynamet project...'
    assert type_ =='.dli_project', "The project type doesn't fit!!"
    dirs=_get_project_directories(path)
    print dirs
    if _check_path(path, dirs):
        for key in dirs.keys():
            os.mkdir(dirs[key])
        target_path=os.path.join(path,'*.zip')
        for rawfile in glob.glob(target_path):
            shutil.move(rawfile, dirs['raw_directory'])
        # create subproject label
        open(os.path.join(path, type_),'w').close()
        # get mass ranges and create subfolders with mass range identifyers
        target_path=os.path.join(path,'*.mzXML')
        peakmaps=[name for name in glob.glob(target_path)]
        for pm in peakmaps:            
            shutil.move(pm, dirs['peakmaps_directory'])
    #move all other files into XCALIBUR_DATA folder
    target_path=os.path.join(path,'*.*')
    for remaining in glob.glob(target_path):
         shutil.move(remaining, dirs['instr_directory'])
    print 'Done'


def check_and_get_project_tree(path):
    """ Function identifies project structure in path and 
        returns type and folder structure of project
    """
    if _is_new_project(path):
        return 
    type_=_check_project_type(path)
    directories=_get_project_directories(path)
    _check_path(path, directories)
    directories['type']=type_
    return directories


def _is_new_project(path):
    expr=os.path.join
    crit=os.path.isfile
    items=os.listdir(path)
    items=[expr(path, i) for i in items]
    if all([crit(i) for i in items]):
        return True


def _check_project_type(path, type_='.dli_project'):
    items=os.listdir(path)
    assert type_ in items, "choosen project folder is"\
                                            " not a dynamet project !!"
    return type_


def project_structure_manager(path, mode='scan'):
    """
    """
    if os is None:
         import pdb; pdb.set_trace()
    directories=check_and_get_project_tree(path)
    if directories:
        return directories
    else:
        print len(glob.glob(os.path.join(path, '*.mzXML')))
        if len(glob.glob(os.path.join(path, '*.mzXML'))):
            create_project(path, mode=mode)
            return check_and_get_project_tree(path)
        assert False, ' WARNING: folder %s contains no peakmaps !!!' %path
            
        