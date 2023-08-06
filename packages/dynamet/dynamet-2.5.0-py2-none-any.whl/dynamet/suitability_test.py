# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 14:50:53 2014

@author: pkiefer
"""
import emzed
import objects_check as checks
import numpy as np
from collections import defaultdict
import helper_funs as helper
import re
from config_manager import manage_config


def build_new_suitability_table():
    t=get_default_table()
    emzed.gui.inspect(t)
    t=t.filter(t.name!='')
    t.addEnumeration
    select_and_add_adducts(t)
    helper.add_mf_ion(t)
    return t
    
        
def get_default_table():
    t=emzed.utils.toTable('name', ['']*12, type_=str)
    t.addColumn('mf', '', type_=str )
    t.addColumn('rtmin', None, type_=float, format_="'%.2fm' %(o/60.0)")
    t.addColumn('rtmax', None, type_=float, format_="'%.2fm' %(o/60.0)")
    t.addEnumeration()
    return t


def select_and_add_adducts(t):
    adducts=emzed.adducts.negative.toTable()
    adduct_names=adducts.adduct_name.values
    names=t.name.values
    selected=[]    
    for i,name in enumerate(names):
        diplay=_uniform_name(name)
        pos=emzed.gui.DialogBuilder('choose adduct %d out of %d' %(i+1, len(t)))\
        .addChoice('%s :'%diplay, adduct_names)\
        .show()
        selected.append(pos)
    t.addColumn('_adduct_names', selected)
    names=[name for name in adducts.getColNames()]
    for name in names:
        if name == 'z_signed':
            def pol(row, t=adducts, col=name):
                v=t.getValue(t.rows[row], col)
                return '-' if v<0 else '+'
            t.addColumn('polarity', t._adduct_names.apply(pol))
        else:
            def fun(row, t=adducts, col=name):
                return t.getValue(t.rows[row], col)
            t.addColumn(name, t._adduct_names.apply(fun))
    _drop_temporary_columns(t)


def _uniform_name(name):
    letters=[l for l in name]
    uniform=''
    for i,letter in enumerate(letters):
        if i==0:
            if len(re.findall('[A-Za-z]', letter)):
                uniform+=letter
            else:
                uniform+='x'
        elif len(re.findall('[A-Za-z0-9]', letter)):
            uniform+=letter
        else:
            uniform+=' '
    return uniform
    
    
def add_mis_to_table(tt,  ref_R=(60000, 400), mztol=0.003):
    required=['mf', 'mf_ion',  'polarity', 'z', 'rtmin', 'rtmax']
    checks.table_has_colnames(required, tt)    
    tables=[]
    _calc_R(tt, ref_R)
    colnames=[n for n in tt.getColNames()]
    pairs=zip(*[list(tt.getColumn(n).values) for n in colnames])   
    pos={colnames[i]:i for i,_ in enumerate(colnames)}
    for i, pair in enumerate(pairs):
        mzs=_get_feature_mz_values(pair[pos['mf_ion']], pair[pos['z']], pair[pos['polarity']],
                                   pair[pos['R']])
        t= emzed.utils.toTable('id', [i]*len(mzs))
        t.addColumn('name', pair[pos['name']], type_=str)
        t.addColumn('mf', pair[pos['mf']], type_=str)
        t.addColumn('mf_ion', pair[pos['mf']], type_=str)
        t.addColumn('mzmin', [mz-mztol for mz in mzs], type_=float, format_='%.4f')
        t.addColumn('mzmax', [mz+mztol for mz in mzs], type_=float, format_='%.4f')
        t.addColumn('mi', range(len(mzs)))
        t.addColumn('z', pair[pos['z']])
        t.addColumn('rtmin', pair[pos['rtmin']], type_=float, format_="'%.2fm' %(o/60)")
        t.addColumn('rtmax', pair[pos['rtmax']], type_=float, format_="'%.2fm' %(o/60)")
        t.addColumn('R', pair[pos['R']], type_=float, format_='%.0f')
        t.addColumn('peakmap', pair[pos['peakmap']])
        tables.append(t)
    return emzed.utils.mergeTables(tables)


def _calc_R(t,ref_r=(60000, 400)):
    t.addColumn('_mass', t.mf_ion.apply(emzed.mass.of), type_=float, format_='%.4f')
    t.addColumn('_mz', t._mass/t.z)
    def calc_(mz, ref_r=ref_r):
        if not ref_r[1]:
            return ref_r[0]
        else:
            return ref_r[0]*np.sqrt(ref_r[1]/mz)
    t.updateColumn('R', t._mz.apply(calc_), type_=float, format_='%.0f')
    _drop_temporary_columns(t)


def _get_feature_mz_values(mf_ion, z, mode,R):
    e=emzed.mass.e
    polarity={'-':e, '+':-e}
    masses=_get_mass_isotopologues_from_mf(mf_ion,R=R)
    mzs=[(m+polarity[mode])/z for m in masses]
    return mzs


def extract_peaks_from_peakmap(t, pm_path, ref_R, mztol=0.003):
    path, inspect=emzed.gui.DialogBuilder('Select Peakmap')\
    .addFileOpen('select peakmap', basedir=pm_path, formats=['mzXML','mzML' ], 
                 help='select a peakmap containing targeted ions')\
    .addBool('inspect peaks', default=True, help='if True table explorer will open '\
            'and you can individually adapt retention time windows')\
    .show()
    pm=emzed.io.loadPeakMap(path)
    t.addColumn('peakmap', pm)
    _update_mz_min_max(t, mztol=mztol)
    checks.table_is_integratable(t)
    n_cpus=checks.get_n_cpus(t)
    t=emzed.utils.integrate(t, 'trapez', n_cpus=n_cpus)
    if inspect:
        emzed.gui.showInformation('you can individually adapt retention time windows'\
                'by moving boundaries in graph and reintegrating the peak subsequently')
        emzed.gui.inspect(t)
    t=add_mis_to_table(t, ref_R)
    t=emzed.utils.integrate(t, 'trapez', n_cpus=n_cpus)
    t=_remove_low_quality_peaks(t)
    emzed.utils.recalculateMzPeaks(t)
    return t


def _update_mz_min_max(t, mztol=0.003):
    for name in ['mzmin', 'mzmax']:
        if t.hasColumn(name):
            t.dropColumns(name)
    mass=emzed.mass
    t.addColumn('_mz', (t.mf.apply(mass.of)+t.mass_shift)/t.z, type_=float)    
    t.addColumn('mzmin', t._mz-mztol, type_=float, format_='%.4f', insertBefore='rtmin')
    t.addColumn('mzmax', t._mz+mztol, type_=float, format_='%.4f', insertBefore='rtmin')
    _drop_temporary_columns(t)

    
def _remove_low_quality_peaks(t, min_area=1e5):
    t1=t.filter(t.area>min_area)
    removed=list(set(t.name.values)-set(t1.name.values))
    emzed.gui.showInformation('Following compounds were removed from test set \n'\
                                'since peaks were missing or quality was too low:\n %s'\
                                %(removed))
    return t1
   
    
def get_test_table(config):
    tb_path=config['project_folders']['toolbox_directory']
    choice=['use current', 'load different', 'build new']
    select=emzed.gui.DialogBuilder('choose ')\
    .addChoice('select test table', choice, help='use current by default is mass calibration table')\
    .show()
    if select == 0:
        test_dic=config['suitability_test']['test_table']
        test_table=helper.dict_to_table(test_dic)
    if select == 1:
        path=emzed.gui.DialogBuilder('load_parameter_table')\
        .addFileOpen('choose_parameter_table', basedir=tb_path, formats=['table'])\
        .show()
        test_table=emzed.io.loadTable(path)
        _check_test_table(test_table)
    if select == 2:
        test_table=build_new_suitability_table()
        helper.save_table(test_table, tb_path)
    config['suitability_test']['test_table']=helper.table_to_dict(test_table)
    return test_table
        
        
def _check_test_table(t):
    required=['name', 'mf', 'rtmin', 'rtmax']
    checks.table_has_colnames(required,t)
    adduct_set=['adduct_name', 'polarity',  'z']
    if not t.hasColumns(*adduct_set):
        #remove remaining columns of adduct set
        [t.dropColumns(name) for name in adduct_set if t.hasColumn(name)]
        select_and_add_adducts(t)
        t.dropColumns('mf_ion')
    if not t.hasColumn('mf_ion'):
        helper.add_mf_ion(t)
        

def suitability_test(table):
    """
    """
    crit=0.8*emzed.MMU
    required=['name', 'id','mz', 'rtmin', 'rtmax', 'R']
    checks.table_has_colnames(required, table)
    add_delta_mz_calc(table)
    add_delta_mz_meas(table)
    pairs=set(zip(table.id.values, zip(table.delta_mz_calc.values, table.delta_mz_measured)))
    check=dict()
    for id_, pair in pairs:
        if len(pair[1]):
            calc=pair[0]
            meas=pair[1]
            check[id_]=tuple([abs(calc[i]-meas[i]) for i in range(len(meas))])
    def fun(v, dic=check):
        return dic.get(v)
    table.addColumn('diff_values', table.id.apply(fun))       
    def control(values, crit=crit):
        return all(v<=crit for v in values)
    table.addColumn('suited', table.diff_values.apply(control))
    result = table.extractColumns('id', 'name', 'diff_values', 'suited')    
    print 'test results:'
    print ''
    print result.uniqueRows()
    print ''


def add_delta_mz_meas(t):
    pairs=zip(t.id.values, t.mz.values)
    dict_=defaultdict(list)
    for id_, mz in pairs:
        dict_[id_].append(mz)
    for key in dict_.keys():
        dict_[key]=tuple(_calculate_delta_values(dict_[key]))
    def fun(v, dict_=dict_):
        return dict_.get(v)
    t.addColumn('delta_mz_measured', t.id.apply(fun))
    

def add_delta_mz_calc(t, min_area=5e5):
    t.addColumn('_temp', t.mf_ion.apply(emzed.mass.of)/(t.z*1.0))
#    t.updateColumn('R', ref_R[0]*(ref_R[1]/t._temp).apply(np.sqrt), type_=float, format_='%d')
    def add_isotopes(table, row, new_col_name):
        return _get_mass_isotopologues_from_mf(t.getValue(row, 'mf_ion', t.getValue(row, 'R')))
    t.addColumn('_masses', add_isotopes, type_=float, format_='%.5f')
    def _mzs(table, row, new_col_name):
        z=t.getValue(row, 'z')
        ms=t.getValue(row, '_masses')
        return [m/z for m in ms]
    t.addColumn('_mzs',_mzs, type_=float, format_='%.5f')
    t.addColumn('delta_mz_calc', t._mzs.apply(_calculate_delta_values))
    _drop_temporary_columns(t)
    
  
def _calculate_delta_values(values):
    assert all([isinstance(v, float) for v in values]), 'values must be floats'
    values=list(values)
    values.sort()
    return tuple([values[i+1]-values[i] for i in range(len(values)-1)])
    
    
def _get_mass_isotopologues_from_mf(mf,R=60000):
    t=emzed.utils.isotopeDistributionTable(mf, R=R)
    return t.mass.values 
    
   
def analyze_test_result(t):
    bad, good, missing=_count_values(t)
    _evaluate_values(bad, good, missing)


def _count_values(t):
    good=0
    bad=0
    missing=0
    # suites has values True, False, None (only 1 mass isotope detected)
    pairs= set(zip(t.id.values, t.suited.values))
    dic=dict()    
    for key, value in pairs:
        if dic.has_key(key):
            if dic[key]:
                dic[key]=value
        else:
            dic[key]=value
    for key in dic.keys():
        if dic[key]==True:
            good+=1.0
        elif dic[key]==False:
            bad+=1.0
        else:
            missing+=1.0
    
    return bad, good, missing

        
def _evaluate_values(bad, good, missing):
    critical=bad/(good+bad)*100
    percent_missing=missing/(good + bad+ missing)*100    
    text=''
    crit=''
    remark=''
    if critical>30:
        emzed.gui.showWarning('more than %s percent of evaluated compounds (%s in total) do not fullfill \n'\
        'the required mass accuracy.\n CHECK FAILED!!' %(round(critical), int(bad+good)))
    if percent_missing>50:
        crit=text+'More than %d % of evaluated compounds (%s in total) had \n'\
        'only monoisotopic peak.\n Choose another peakmap or use a test_table with'\
        'different compounds!!' %(round(critical), int(bad+good+ missing))
    if good+bad<5:
        remark='The number of evaluated compounds is low !!'\
        ' Consider enlarging compound number.'
    info='test_table compounds (%s out of %s) fullfill mass'\
    ' accuracy requirement!' %(int(good), int(good+bad))
    emzed.gui.showInformation(info+'\n'+crit+ '\n'+remark)
        
#
#  MAIN FUNCTION
#
#######################################################    
def main_suitable(config):
    test_table=get_test_table(config)
    ref_r=config['suitability_test']['ref_R']
    pm_path=config['project_folders']['peakmaps_directory']
    mztol=config['suitability_test']['isol_width']
    test_table=extract_peaks_from_peakmap(test_table, pm_path, ref_r, mztol)
    suitability_test(test_table)    
    analyze_test_result(test_table)
    manage_config(None, config=config)
    

###########################
#helper_fun

def _drop_temporary_columns(t):
    t.dropColumns(*[name for name in t.getColNames() if name.startswith('_')])