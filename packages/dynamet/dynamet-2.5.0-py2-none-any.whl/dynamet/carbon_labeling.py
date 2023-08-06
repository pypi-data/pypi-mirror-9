# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 12:59:30 2013

@author: pkiefer
"""
import emzed
from emzed.core.data_types import Table
import objects_check as checks
import numpy as np
import iso_corr
import helper_funs as helper
from collections import defaultdict

def get_feature_carbon_labeling(tables):
    assert isinstance(tables, list)
    def fun(t):
        assert isinstance(t, Table), 'tables in not list of tables'
    [fun(t) for t in tables]
    required=['mz', 'source', 'feature_id', 'area', 'z']
    assert isinstance(tables, list), 'input must be list of tables'
    for table in tables:
        assert isinstance(table, Table), 'object is not of class table'
        checks.table_has_colnames(required, table)    
    timepoints=merge_tables_by_time(tables)
    samples=[calculate_carbon_labeling(t) for t in timepoints]
    samples=emzed.utils.mergeTables(samples).splitBy('source')
    for t in samples:
        t.replaceColumn("feature_id", t.feature_id.apply(lambda v: int(v)), format_="%d")
        t.title=t.source.uniqueValue()
    return samples

def merge_tables_by_time(tables):
    merged=emzed.utils.mergeTables(tables, force_merge=True)
    return merged.splitBy('time')    

def calculate_carbon_labeling(t):
    """ carbon labeling is calculated by column mz0 if mz0 was determined in sample t0=0
        if the metabolite was not determined in sample t0m the smallest isotope is chosen.
        
    """
    assert isinstance(t, Table), 'tables in not list of tables'
    
    required=['feature_id', 'mz', 'mz0', 'feature_mz_min', 'area', 'source', 'num_c']
    checks.table_has_colnames(required, t)    
    print 'Labeling of timepoint %d' %t.time.uniqueValue()
    helper.get_num_isotopes(t)
    # remove all features where number of C could'nt be estimated:
    t=t.filter(t.num_c.isNotNone())
    features=t.splitBy("feature_id")
    for feature in features:
        sum_up_isotope_areas(feature)
        feature.updateColumn("mi_fraction", feature.summed_isotope_area/feature.area.sum(), 
                             type_=float)
        if all(v != None for v in feature.area.values):
#        print feature.mi_frac.values
        # estimate number of carbon atoms from natural labeling
            correct_mi_frac(feature)
        else:
            feature.addColumn('mi_frac_corr', None, type_=float, format_='%.2f')
#        print feature.mi_frac_corr.values
        feature.updateColumn('_temp', feature.mi_frac_corr*feature.num_isotopes)
        try:
            feature.updateColumn("no_C13", feature._temp.sum(), format_="%.2f", type_=float)
        except:
            feature.updateColumn("no_C13", None, type_=float)
#            assert False
        feature.updateColumn("C13_fraction", feature.no_C13/feature.num_c, format_="%.2f", 
                             type_=float)
        feature.dropColumns('_temp')
    return emzed.utils.mergeTables(features, force_merge=True)
    
def sum_up_isotope_areas(t):
    t.addColumn('_key', zip(t.time.values, t.num_isotopes.values))
    pairs=zip(t._key.values, t.area.values)
    dic=defaultdict(int)
    for tup in pairs:
        dic[tup[0]]+=tup[1]
    def fun(v, dic=dic):
        return dic.get(v)
    t.addColumn('summed_isotope_area', t._key.apply(fun), type_=float,  format_='%.2e',
                insertAfter='area')
    t.dropColumns('_key')
                
    
    
def correct_mi_frac(t):
    def fun(v):
        return 0 if v is None else v
    assert t.hasColumn('mi_fraction'), 'No of estimated C atoms in ion is missing'
    if t.hasColumn('num_c'):
        n=t.getColumn('num_c').apply(fun, filter_nones=False).uniqueNotNone()
        if n and n<=170: #170 = limit für anzahl der C atome !!
            # BAUSTELLE 
            frac=np.zeros((n+1))
            for i in range(len(t)):
                if n+1<len(t):
                    print t.feature_id.values
                try:
                    j=t.getColumn('num_isotopes').values[i]
                except:
                    emzed.gui.inspect(t)
                    print 'j, i', j, i
                try:
                    frac[j]=t.getColumn('mi_fraction').values[i]
                except:
#                    emzed.gui.inspect(t)
                    print 'j, i', j, i
#                    t.print_()
            print n, frac
#            if all(frac):
            frac,_=iso_corr.compute_distribution_of_labeling(frac, n)
            mi=t.getColumn('num_isotopes').values
            value=[frac[i] for i in mi]
#            else:
#                value=None
        else:
            value=None
    t.updateColumn('mi_frac_corr', value, format_='%.2f', type_=float)

        
    