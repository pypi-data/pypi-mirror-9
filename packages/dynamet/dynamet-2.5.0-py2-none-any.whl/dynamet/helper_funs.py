# -*- coding: utf-8 -*-
"""
Created on Tue Mar 04 16:11:34 2014

@author: pkiefer
"""
import emzed
import re
from emzed.core.data_types import Table, PeakMap 
import objects_check as checks
import json
import os
import glob
import numpy as np

def update_mz0(t):
    """ function should only be applied to natural labeled samples
    """
    required=['feature_id', 'mz', 'area']
    checks.table_has_colnames(required, t)
    t.addColumn('max_area', t.area.max.group_by(t.feature_id))
    t.addColumn('min_mz', t.mz.min.group_by(t.feature_id))
    t.updateColumn("mz0", ((t.area==t.max_area) & (t.mz==t.min_mz)).thenElse(t.min_mz, None),
                                                                           format_="%.5f")
    t.replaceColumn('mz0', t.mz0.max.group_by(t.feature_id))
    t.dropColumns('max_area', 'min_mz')


def get_monoisotopic_mass(t, insert_before=None):
    required=['z', 'mz0', 'adduct_mass_shift']
    checks.table_has_colnames(required, t)
    def fun(table, row, new_col_name):
        expr=table.getValue
        mz0 = expr(row, 'mz0')
        z = expr(row, 'z')  
        mass_shift = expr(row, 'adduct_mass_shift')
        if isinstance(mass_shift,tuple):
            if mz0 and z and any(mass_shift):
                values=[ round((mz0*z - ad), 5) for ad in mass_shift if ad]
                return tuple(values) 
        return (None, )
    t.addColumn('possible_m0', fun, insertBefore=insert_before)
    

def update_column_by_dict(t, col, ref_col, dict_):
    """ 
    """
    _type=t.getColType(col)
    if t.hasColumn(col):        
        t.replaceColumn(col, (t.getColumn(ref_col).apply(dict_.get)).ifNotNoneElse(t.getColumn(col)),
                        type_=_type)
    else:
        t.addColumn(col, t.getColumn(ref_col).apply(dict_.get))


def extract_dict_from_table(t, ref_col, target_col):
    dict_=dict()
    pairs=set(zip(t.getColumn(ref_col).values, t.getColumn(target_col).values))
    for key,value in pairs:
        if dict_.has_key(key):# and value:
            if (set(dict_[key])-set([value]))==set(dict_[key]):
                new=list(dict_[key])            
                new.append(value)
            dict_[key]=tuple(new)
        else:
            dict_[key]=tuple([value])
    return dict_


def table_to_dict(t):
    """ converts table into dictionary ('colname', values). Peakmaps are lost
    """
    assert isinstance(t, Table), 'item must be Table'
    colnames=[name for name in  t.getColNames() if name!='peakmap']
    coltypes=[str(t.getColType(name)) for name in colnames]
    colformats=[t.getColFormat(name) for name in colnames]
    layout=zip(colnames, coltypes, colformats)
    table_dict=dict()
    for name in colnames:
        table_dict[name]=t.getColumn(name).values
    table_dict['layout']=layout
    return table_dict
    
    
def dict_to_table(dic):
    """ converts dictionary into table with colnames dict.keys() and column values must be 
        lists, tuples of the same length or unique values.
    """
    assert isinstance(dic, dict), 'item must be dictionary'
    assert dic.has_key('layout'), 'dictionary is not a table dictionary'
    colnames=[v[0] for v in dic['layout']]
    assert set(dic.keys())-set(colnames)==set(['layout']), 'colnames are missing'
    types=[v[1] for v in dic['layout']]
    formats=[v[2] for v in dic['layout']]
    t=emzed.utils.toTable(str(colnames[0]), dic[colnames[0]], type_=convert_str_to_type(types[0]),
                          format_=formats[0])
    for i,name in enumerate(colnames):
        if i: 
            t.addColumn(name, dic[name], type_=convert_str_to_type(types[i]), format_=formats[i])
    return t


def convert_str_to_type(str_type):
    objects=[1, '1', 1.0, (1,), [], ]
    dic={str(type(o)): type(o) for o in objects }
    return dic[str_type]
    
    
def get_num_isotopes(t):
    assert isinstance(t,Table), 'object is not of class table'
    # the funcion is mainly developped for Dynamet, where feature_mz_min is the lowest m/z value 
    # overall samples and mz0 is the lowest mz value of natural labeled sample at t=0. 
    # feature_mz_min is selected if the feature was not detected in the t=0 sample. 
    _check_consistency(t)
    def _help(x):
        return int(round(x,0))
    if not len(t):
        return t
    expr1=(t.mz-t.mz0)*t.z
    expr2=(t.mz-t.feature_mz_min)*t.z
    t.addColumn("_temp", t.mz0.isNotNone().thenElse(expr1, expr2))
    t.updateColumn("num_isotopes", t._temp.apply(_help), format_="%d")
    t.dropColumns("_temp") 


def _check_consistency(t, mztol=0.005):
    required=['feature_id', 'mz0', 'mz', 'z', 'feature_mz_min']
    checks.table_has_colnames(required, t)    
    t.addColumn('min_mz', t.mz.min.group_by(t.feature_id))
    check=zip(t.min_mz.values, t.mz0.values, t.feature_mz_min.values)
    for a,b,c in check:
        if a and b and c:
            assert a-b>=-mztol
            assert ((-mztol<=(b-c)<=mztol) | (b-mztol<c)) 
        elif a and b:
            assert a-b>=-mztol
        elif a and c:
            assert a-c>=-mztol
    t.dropColumns('min_mz')


def determine_charge_state(t, z_limits=(1,3)):
    """ in place determines charge state of feature from peak mass differences 
    """
    zmin, zmax=z_limits
    z_range=range(zmin, zmax+1)
    assert all([isinstance(z, int) for z in z_range]), 'z values must be integers'
    assert isinstance(t, Table), 't is not of Type Table'
    check_charge_state(t, z_range)
    t.replaceColumn('z', (t._z==t.z).thenElse(t.z, t._z))
    t.dropColumns('_z')


def check_charge_state(t, z_range=range(1,4)):
    """ plausibility check 
    """
    required=['mz', 'feature_id']
    checks.table_has_colnames(required, t)
    t.updateColumn('_z', None)
    t.updateColumn('_diff', t.mz-t.mz.min.group_by(t.feature_id))
    for z in z_range:
        t.updateColumn('_temp', (t._diff*z).apply(lambda v: round(v,1)))
        t.updateColumn('_select', (t._temp==t._temp.apply(int)).thenElse(True, False))
        t.updateColumn('_select', (t._select.sum.group_by(t.feature_id)==t._select.len.group_by\
                                  (t.feature_id)).thenElse(True,False))
        t.updateColumn('_z', (t._z.isNone() & (t._select==True)).thenElse(z,t._z))
        t.updateColumn('_z', (t._z.len.group_by(t.feature_id)<=1).thenElse(0, t._z))
    t.dropColumns('_diff', '_select', '_temp')
    

def removePostfixes(t):
    """ in place: all redundant columns as well as unnecessary postfixes 
        of table t are removed
    """
    postfixes=t.findPostfixes()
    postfixes.remove("")
    with_pstfx=[]
    colnames = [name for name in t.getColNames()]
    for fix in postfixes:
        names=[name.split(fix)[0] for name in t.getColNames() if name.endswith(fix)]
        with_pstfx.extend(names)
    unique=set(with_pstfx).difference(set(colnames))
    for colname in unique:
        for fix in postfixes:
            if t.hasColumn(colname+fix):
                t.renameColumns(**{colname+fix:colname})


def time_label():
    """ gives string of current time back.  can be used e.g. to label filenames
    """
    import time
    x=time.localtime()
    year=str(x.tm_year)
    month=_add_zero(str(x.tm_mon))
    day=_add_zero(str(x.tm_mday))
    hour=_add_zero(str(x.tm_hour))
    mins=_add_zero(str(x.tm_min))
    secs=_add_zero(str(x.tm_sec))
    label=year+month+day+"_"+hour+"h"\
           + mins+"m"+secs+"s"
    return label
    
    
def _add_zero(item):
    if len(item)==1:
        return '0'+ item
    return item

    
def save_dict(dic, name, path=None, overwrite=False):
    """ Saves dictionary `dic` as `name.json` in path `path`"""
    if not path:
        path=emzed.gui.askForDirectory(caption='choose saving folder')
    if not name.endswith('.json'):
        name=name+'.json'
    name = os.path.join(path, name)
    print 'saving path: ', name
    if  os.path.exists(name) and not overwrite:
        assert False, '% s already exists. Please choose different name. '\
                    'To overwrite existing file choose overwrite=True'
    with open (name, 'w') as fp:
        json.dump(dic, fp, indent=4, encoding='latin-1')
    fp.close()


def load_dic(path=''):
    "loads dictionary saved as .json if path, else default dialog is opened"
    if os.path.isfile(path):
              if os.path.basename(path).endswith('.json'):
                pass
    else:
        path=emzed.gui.askForSingleFile(startAt=path, extensions=['json'], 
                                        caption='load dictionary (.json)')
    if path:
        with open(path, "r") as fp:
            return  convert(json.load(fp))


def convert(input, encode='latin-1'):
    """ converts strings in unicode into encode format default=latin-1
    """
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encode)
    else:
        return input

   
def dic_has_keys(dic, keys):
    assert isinstance(dic, dict) 
    diff=set(keys)-set(dic.keys())
    if diff:
        show=list(diff)
        missing=show[0]
        for key in show[1:]:
            missing=missing+', '+key
    assert len(diff)==0, 'key(s) %s are missing' %missing


def transfer_column_between_tables(t_source, t_sink, data_col, ref_col, insert_before=None ):
    """ (t_source, t_sink, data_col, ref_col)adds values from column data_col from Table 
        `t_source` to Table `t_sink` via common reference
    column `ref_col`. If column `data_col` exists already in t_sink an assertion occurs
    """
    #    checks
    assert isinstance(t_source, Table), 't_source is not of Type table'
    assert isinstance(t_sink, Table), 't_sink is not of Type table'
    missing=set([data_col, ref_col])-set([n for n in t_source.getColNames()])
    assert len(missing)==0, 'column(s) %s are missing in Table %s' %(missing, t_source)
    assert t_sink.hasColumns(ref_col), 'column %s is missing in Table %s' %(ref_col, t_sink)
    assert t_sink.hasColumns(data_col)==False, 'column %s exists already in Table %s' \
                                                %(data_col, t_sink)
    type_=t_source.getColType(data_col)
    format_=t_source.getColFormat(data_col)
    pairs=set(zip(t_source.getColumn(ref_col).values, t_source.getColumn(data_col).values))
    ref2data={v[0]:v[1] for v in pairs}
    def _add(v, dic=ref2data):
        return dic.get(v)
    t_sink.addColumn(data_col, t_sink.getColumn(ref_col).apply(_add), type_=type_, format_=format_, 
                     insertBefore=insert_before )


def peakmap_as_table(pm):
    """ converts peakmap pm into table format
    """
    assert isinstance(pm, PeakMap), 'item must be of type PeakMap!'
    t=emzed.utils.toTable('peakmap', [pm])
    t.addColumn('unique_id', pm.uniqueId())
    t.addColumn('full_source', pm.meta['full_source'])
    t.addColumn('source', pm.meta['source'])
    return t

    
def label_peakmap_processing(pm, process):
    assert isinstance(process, str), 'processing label must be string'
    assert isinstance(pm, PeakMap)
    key='processing'
    if pm.meta.has_key('processing'):
        pm.meta[key]=pm.meta[key].union(set([process]))
    else:
        pm.meta['processing']=set([process])


def save_table(t, tb_path):
    name, overwrite=emzed.gui.DialogBuilder('Save test_table')\
    .addString('file name', default='test_table')\
    .addBool('overwrite existing file', default=True)\
    .show()
    name=_check_filename(name)
    path=os.path.join(tb_path, name)
    emzed.io.storeTable(t, path, forceOverwrite=True)

    
def _check_filename(name):
    # 1. name must not start with digit
    pattern='([A-Za-z_][A-Za-z0-9_-]+).table*'
    matchs=re.match(pattern, name)
    while not matchs:
        emzed.gui.showWarning('Filenames must not start with digits and'\
             'should only contain charachters A-Z, a-z, 0-9, _,-'\
        ' Please modify your filename!')
        name=emzed.gui.DialogBuilder('modify file name')\
        .addString('file name', default=name)\
        .show()
        matchs=re.match(pattern, name)
    if name.endswith('.table'):
        return name
    else: 
        return name+'.table'    
        
        
def enhanced_save_table(t,path, forceOverwrite=True):
    assert isinstance(t, Table), '%s is not of type Table' %path
    if os.path.exists(path):
        if not forceOverwrite:
            directory, name=os,path.split(path)
            name,ending=name.split('.')
            name=name+'_'+time_label()+'.'+ending
            path=os.path.join(directory, name)
        else:
            print 'EXISTING  TABLE WILL BE OVERWRITEN!'
    emzed.io.storeTable(t, path=path, forceOverwrite=forceOverwrite)

           
def listfind(values, value):
    assert isinstance(values, list), 'values is not a list' 
    return [i for i, f in enumerate(values) if f == value]


def get_isotopologous_mass_distance(t, id_column='feature_id'):
    assert isinstance(t, Table)
    assert t.hasColumns('mz', 'z')
    if not t.hasColumns('id'):
        t.addEnumeration()
    t.addColumn('delta_m', None, type_=float, format_='%.5f')
    features=t.splitBy(id_column)
    dic=dict()
    for f in features:
        f.sortBy('mz')
        z=f.z.uniqueValue()
        if z:
            keys=f.id.values
            masses=[mz*z for mz in f.mz.values]
            delta=delta_values_from_list(masses)
            for i, key in enumerate(keys):
                dic[key]=delta[i]
    update_column_by_dict(t, 'delta_m', 'id', dic)

     
def delta_values_from_list(numbers):
    shifted=[numbers[0]]
    shifted.extend(numbers[:-1])
    return [(numbers[i]-shifted[i]) for i in range(len(numbers))]    
  

def get_natural_isotopes_mass_shifts_from_mf(mf, R=6e4, minp=0.01):
    t=emzed.utils.isotopeDistributionTable(mf, R=R, minp=minp)
    delta_m=delta_values_from_list(t.mass.values)
    t.addColumn('delta_m', delta_m)
    return zip((mf,)*len(t), t.delta_m.values)
    
    
def test_spec_delta(pm, mz1, mz2, mztol=0.003):
    values=[]
    for spec in pm.spectra:
        v1 = extract_best_peak(spec, mz1, mztol)
        v2 = extract_best_peak(spec, mz2, mztol)
        if (v1!=None and v2!=None):
            values.append(abs(v1-v2))
    return float(np.average(values)), np.std(values), len(values)


def extract_best_peak(spec, mz, mztol):
    peaks = spec.peaksInRange(mz-mztol, mz+mztol)
    delta=[(peak[0],(peaks[i][0]-mz)) for i, peak in enumerate(peaks)]
    return min(delta, key=lambda v: v[0])[0] if delta else None
 
   
def remove_files_from_path(path, type_='*.*'):
    path=os.path.join(path,type_)    
    pathes=glob.glob(path)
    if len(pathes):
        for p in pathes:
            os.remove(p)


def load_table_items(path):
    """ determines type from ending. Can load tables saved as json, table, and csv, 
    assertion if file type  does not fit. Ouput is a Table.
    """
    assert os.path.isfile(path), 'path %s does not exits' %path
    allowed=['json', 'table', 'csv']
    
    _, ending=os.path.basename(path).split('.')
    assert ending in allowed, '%s is not an accepted file format (%s)'%(ending, allowed)
    if ending == 'table':
        return emzed.io.loadTable(path)
    elif ending == 'csv':
        return emzed.io.loadCSV(path)
    else:
        dic=load_dic(path)
        return dict_to_table(dic)
    
##########################################################################################
def add_mf_ion(t):
    required=['mf', 'adduct_name']
    checks.table_has_colnames(required, t)
    def mf_ion(table, row, new_col_name):
        return _build_mf_ion(t.getValue(row, 'mf'), t.getValue(row, 'adduct_name'))
    t.addColumn('mf_ion', mf_ion, insertAfter='mf')    


def _build_mf_ion(mf, adduct):
    mf_plus,mf_minus=_adduct_mf(adduct)
    mf_minus="-"+mf_minus
    return emzed.utils.addmf(mf,mf_plus,mf_minus)


def _adduct_mf(entry):
    start= entry.find("M")+1
    entry=entry[start:]
    set_=["",""]
    for parts in entry.split("+"):
        res=[mod for mod in parts.split("-")]
        if len(res)==1:
            set_[0]=set_[0]+_turn_order(res[0])
        if len(res)>1:
           set_[0]=set_[0]+_turn_order(res[0])
           for add in res[1:]:
               set_[1]=set_[1]+_turn_order(add)
    return set_


def add_observed_adducts(adduct):
    """
    """
    mass=emzed.mass
    additional=['M+H3PO4-H']
    phos=emzed.utils.toTable('adduct_name', additional)
    phos.addColumn('mass_shift', [mass.of('H3PO4')-mass.p])
    phos.addColumn('z_signed', [-1])
    phos.addColumn('z', [1])
    return emzed.utils.mergeTables([adduct,phos], reference_table=adduct)

def _turn_order(string):
    if string:
        num= re.split('[A-Z][a-z]?', string)[0]
        element=re.split('[1-9][0-9]?', string)[-1]
        return element+num
    else:
        return string


def determine_fgrouper_rttol(tables):
    """ the value is set to fwhm/2
    """
    fwhms=[]
    [fwhms.extend(t.fwhm.values) for t in tables]
    return int(round(np.median(fwhms)*0.5))
############################################################################################