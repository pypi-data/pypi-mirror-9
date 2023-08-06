# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 14:03:23 2014

@author: pkiefer
"""
from sample_feature_grouper import build_reference_table
import emzed
import objects_check as checks
import numpy as np


def extract_global_features(tables, config, sample_order, t0_name=None):
    if not t0_name:
        t0_name=_get_t0_name(tables, sample_order)
    sort_tables_by_sample_order(tables, sample_order)
    add_time_order_to_tables(tables, sample_order)
    t_ref=build_reference_table(tables, parameters=config)
    resulting=get_global_features(tables, t_ref, config)
    return resulting


def sort_tables_by_sample_order(tables, sample_order):
    def _sort(t, order=sample_order):
        id_=t.source.uniqueValue()
        i=[i for i,v in enumerate(sample_order['sample_names']) if v==id_][0]
        return sample_order['sample_order'][i]
    tables.sort(key=_sort)


def _get_t0_name(tables, sample_order):
    i=[i for i,v in enumerate(sample_order['time']) if v==0.0]
    assert len(i)>0, 'natural labeled sample at t=0.0s is missing!!'
    if len(i) >1:
        sample_names=[sample_order['sample_names'][v] for v in i]
        t0s=[(t.source.uniqueValue(), len(t)) for t in tables if t.source.uniqueValue() in sample_names]
        print t0s
        print max(t0s, key=lambda v: v[1])
        return max(t0s, key=lambda v: v[1])[0]
        
    i=i[0]
    return sample_order['sample_names'][i]


def get_global_features(tables, t_ref, parameters):
        return [extract_features_by_ref(t, t_ref, parameters=parameters) for t in tables]


def extract_features_by_ref(t, ref, parameters=None):
    if not parameters:
        rttol=25 #sec
        mztol=0.003 #U
        rel_min_area=0.01
    else:
        rttol = parameters['rt_tol']
        mztol = parameters['isol_width']
        rel_min_area=parameters['rel_min_area']
    pm=t.peakmap.uniqueValue()
    time=t.time.uniqueValue()
    order=t.order.uniqueValue()
    sample=ref.copy()
    sample.addColumn('mzmin', sample.mz-mztol/2.0, format_='%.5f')
    sample.addColumn('mzmax', sample.mz+mztol/2.0, format_='%.5f')
    sample.addColumn('rtmin', sample.rt-rttol/2.0, format_="'%.2fm' %(o/60.0)")
    sample.addColumn('rtmax', sample.rt+rttol/2.0, format_="'%.2fm' %(o/60.0)")
    sample.addColumn('peakmap', pm)
    sample.addColumn('time', time, type_=float)
    sample.addColumn('order', order, type_=int)
    sample.addColumn('unique_id', t.unique_id.uniqueValue(), format_=None)
    sample.addColumn('source', t.source.uniqueValue())
    fwhm=np.median(t.fwhm.values)
    sample=checks.enhanced_integrate(sample, fwhm=fwhm)
    sample=sample.filter(sample.area>0)
    # remove all peaks below rel_min_area
    sample.addColumn('_max_area', sample.area.max.group_by(sample.feature_id))
    sample=sample.filter(sample.area/(sample._max_area*1.0) >= rel_min_area)
    emzed.utils.recalculateMzPeaks(sample)
    _update_rt(sample)
    return _cleanup(sample)


def _update_rt(t):
    t.addColumn('_rt', (t.method=='emg_exact').thenElse(t.params.apply(lambda v: v[1]), t.rt))
    t.replaceColumn('_rt', t._rt.median.group_by(t.feature_id))
    t.replaceColumn('rtmin', t.rtmin-t.rt+t._rt)
    t.replaceColumn('rtmax', t.rtmax-t.rt+t._rt)
    t.replaceColumn('rt', t._rt.ifNotNoneElse(t.rt))
    t.dropColumns('_rt')


def _cleanup(t):
    colnames_order = ['id', 'feature_id', 'source', 'time', 'order', 'adduct_group', 'possible_adducts', 
                      'adduct_mass_shift', 'possible_m0', 'rt', 'rtmin', 'rtmax', 'fwhm', 'mz', 
                      'mzmin', 'mzmax', 'mz0', 'feature_mz_min', 'z', 'num_isotopes', 'method',
                      'area', 'rmse', 'params', 'peakmap', 'unique_id']
    return t.extractColumns(*colnames_order)

    
def add_time_order_to_tables(samples, sample_order):
    tuples=zip(sample_order['sample_names'], sample_order['sample_order'], sample_order['time'])
    def time(v, values=tuples):
        select=[value for value in values if value[0]==v]
        if len(select)==1:
            return select[0][2]
    def order(v, values=tuples):
        select=[value for value in values if value[0]==v]
        if len(select)==1:
            return select[0][1]
    for s in samples:
        s.updateColumn('time', s.source.apply(time), type_= float, format_='%.2fs')
        s.updateColumn('order', s.source.apply(order), type_= int, format_='%d')
            
    