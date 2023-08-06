# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 13:10:57 2013

@author: pkiefer
"""
from emzed.core.data_types import PeakMap, Table
import emzed
import numpy as np


def table_has_colnames(colnames, table, postfixes=None):
    """table_has_colnames(colnames, table, postfixes=None) checks whether
      colnames are present in table. if  postfixes is none: at least one
      complete set of required prefixes must be present
    """
    assert isinstance(colnames, list), "parameter colnames is not a list"
    for name in colnames:
        assert isinstance(name, str), "list element %s is not a string" \
                                        % str(name) 
    assert isinstance(table, Table), "object table must be emzed table expression !!"
    assert isinstance(postfixes, list) or postfixes==None, "postfixes must be"\
                                        "list or None"
    if not postfixes:
        postfixes = table.supportedPostfixes(colnames)
    if not postfixes:
        postfixes=['']
    for postfix in postfixes:
        assert isinstance(postfix, str), "parameter postfixes must be list "\
                                        "of strings"
        print postfix
        required=[n + postfix for n in colnames]
        missing=set(required)-set([name for name in table.getColNames()])
        if len(missing):
            columns=''
            for name in missing:
               if not columns:
                   columns=name
               else:
                   columns=columns+ ' ' + name 
            assert False, "column(s) % s is (are) missing" % columns

    
def table_is_integratable(t):
    assert isinstance(t, Table), "t must be Table expression"
    required=['rtmin', 'rtmax', 'mzmin', 'mzmax', 'peakmap']
    return colname_type_checker(t, required)
    

def is_ff_metabo_table(t):
    
    """verifies wheather table column names and column types correspond
    to featureFinderMetabo output table
    
    """
    assert isinstance(t, Table), "item must  be Table"
    
    required=['id', 'feature_id', 'mz', 'mzmin', 'mzmax', 'rt', 'rtmin',
                  'rtmax', 'intensity', 'quality', 'fwhm', 'z', 'peakmap',
                  'source']
    table_has_colnames(required, t, postfixes=[''])
    if len(set(t.getColNames())-set(required)):
        print 'WARNING: TABLE %s HAS ADDITIONAL COLUMNS!' %t.source.uniqueValue()
    return colname_type_checker(t, required)


def colname_type_settings():
    name_type={'mz': float, 'mzmin': float, 'mzmax': float, 
               'rt': float, 'rtmin': float, 'rtmax': float,
               'fwhm': float, 'quality': float, 'intensity': float, 
               'area': float, 'rmse': float, 'feature_id': int,
               'id': int, 'm0': int, 'params': object, 'z': int,
               'source': str, 'method': str, 'peakmap': PeakMap, }
    return name_type


def colname_type_checker(t, colnames):
    postfixes=t.supportedPostfixes(colnames)
    type_settings=colname_type_settings()
    for postfix in postfixes:
        for colname in colnames:
            assert t.hasColumn(colname+postfix)==True,'Column %s is missing' %colname+postfix
            # fix peakmap can be of type object in older tables 
            if colname=='peakmap':
                if t.getColType(colname+postfix)==object:
                    
                    pms=list(set(t.getColumn(colname+postfix).values))
                    for pm in pms:
                        assert isinstance(pm, PeakMap), 'Object(s) in column %s is not '\
                        'of type Peakmap' %colname+postfix
                    t.setColType(colname+postfix, PeakMap)
            is_col_type=t.getColType(colname+postfix)
            exp_col_type=type_settings[colname]
            assert is_col_type == exp_col_type, 'Column %s is of'\
            'type %s and not of type %s' %(is_col_type, exp_col_type )
    return True

    
def item_polarity(items):
    """
    returns unique polarity value ´+´ or ´-´ from list of peakmaps or tables
    and raises an assertionError if False
    """
    assert isinstance(items,list), "items must be list of PeakMaps or Tables"
    polarity=None
    pms=[]
    check=[isinstance(item, Table) for item in items]
    print check
    if set(check)==set([True]):
       for t in items:
            postfixes=t.supportedPostfixes(["peakmap"])
            for postfix in postfixes:
                peakmap="peakmap"+postfix
                peakmaps=list(set(t.getColumn(peakmap).values))
                pms.extend(peakmaps)
       items=pms
    check=[isinstance(item, PeakMap) for item in items]
    if set(check)==set([True]):
       polarity=[pm.polarity for pm in items]
    if polarity:
        assert len(set(polarity))==1, "polarity in peakmap not unique"
        return polarity[0]
    else: 
        assert False, "Item list is neither of type PeakMap nor of type Table"


def monotonic(t, sort_col, target_col, ascending=True):
    """ checks for strictly monotony in target_col after sorting table rows by sort_col, sortBy is
    always ascending; ascending 
    
    """
    assert isinstance(t,Table)
    assert isinstance(ascending, bool)
    required=[sort_col, target_col]
    table_has_colnames(required, t)
    t.sortBy(sort_col, ascending=True)
    for name in required:
        dx=np.diff(t.getColumn(name).values)
        if ascending:
            assert np.all(dx>=0), 'values of column %s are not mononotonicaly ascending' \
            % name
        else:
            assert np.all(dx<=0), 'values of column %s are not mononotonicaly descending'\
            % name


def unique_id_table(table,colName):
    """uniqueIdTab(table,colName): removes all rows with redundand entries 
    in column colName from table"""
    unique=[]
    table = table.copy()
    if colName=="mf":
        table.addColumn("mf_normalized", table.mf.apply(_normalize_mf))    
        tables_by_colN = table.splitBy("mf_normalized")
    else:
        tables_by_colN=table.splitBy(colName)
        
    for t in tables_by_colN:
        t.addEnumeration("_id")
        t = t.filter(t._id == t._id.min)
        t.dropColumns("_id")
        unique.append(t)
    if len(unique)>0:
        return emzed.utils.mergeTables(unique)
    else:
        return table

        
def _normalize_mf(mf):
    """Alphabetic order of elements in MF: 
    """
    import re
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    # -> z.b [ (Ag, ""), ("Na", "2")]
    fields.sort()
    normalized = [ sym + ("1" if count=="" else count) for (sym, count) in fields ]
    # -> ["Ag1", "Na2" ]
    return "".join(normalized)


def is_list_of_tables(tables):
    assert isinstance(tables, list), 'function only acceps list of tables'
    assert all([isinstance(t, Table) for t in tables]), 'at least 1 object in list is not a table!'

#########################################################################################
# enhanced_integration
def  enhanced_integrate(t, step=1, fwhm=None):
    if not fwhm:
        is_ff_metabo_table(t)
    else:
        table_is_integratable(t)
        if not t.hasColumn('fwhm'):        
            t.addColumn('fwhm', fwhm)
    emg1=special_integrate(t, a=1*step)
    emg2=special_integrate(t, a=2*step)
    a1=emg1.area.values
    a2=emg2.area.values
    diff=[(a1[i]-a2[i])/(a2[i]+1.0)*100 for i in range(len(a1))] #avoiding zero devision
    emg1.addColumn('_diff', diff)
    emg2.addColumn('_diff', diff)
    good2=emg2.filter(emg2._diff.inRange(-10,10) & (emg2.area>100))
    good2.dropColumns('_diff')
    good1=emg1.filter((emg1._diff<-10) & (emg1.area>100))
    good1.dropColumns('_diff')
    found=set([])
    if len(good1) and len(good1):
        a=list(good2.id.values)
        a.extend(good1.id.values)
        found=set(a)
    elif len(good1) and not len(good2):
       found=set(good1.id.values)
    elif len(good2) and not len(good1):
        found= set(good2.id.values)
    fids=list(set(t.id.values)-found)
    remaining=t.filter(t.id.isIn(fids))
    if len(remaining):
        n_cpus=get_n_cpus(remaining)
        remaining=emzed.utils.integrate(remaining, 'trapez', n_cpus=n_cpus)
        return emzed.utils.mergeTables([good2, good1, remaining], force_merge=True)
    return emzed.utils.mergeTables([good2, good1], force_merge=True)
        
        
def special_integrate(t, a=1):
    t1=t.copy()
    t1.replaceColumn('rtmin', t1.rt-a*t1.fwhm, format_="'%.2fm' %(o/60.0)")
    t1.replaceColumn('rtmax', t1.rt+a*t1.fwhm, format_="'%.2fm' %(o/60.0)") 
    n_cpus=get_n_cpus(t)
    return emzed.utils.integrate(t1, 'emg_exact', n_cpus=n_cpus)
    
    
def get_n_cpus(t, max_cpus=8):
   from multiprocessing import cpu_count
   n_cpus=cpu_count()-1 if cpu_count()>1 else cpu_count()
   if n_cpus>max_cpus:
       n_cpus=max_cpus
   estimated=int(np.sqrt(len(t)/250.0))
   if estimated<=n_cpus:
       return estimated
   return n_cpus
   
    