# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:38:58 2014

@author: pkiefer

principles: imput samples tables, and parameter dicitionarys. Tool builds dictionarys with 
identification results, fitting results and plots
"""
import emzed 
import numpy as np
from scipy import cluster
import idms_metabolite_identifyer as idms_ident
from scipy.optimize import curve_fit
import labeling_plots as plots


def main_data_analysis(samples, p_ident, p_data_analysis, sample_order, result_path):
    """main data analysis function
    """
    ident_dict=idms_ident.identify_metabolites(samples, p_ident)
    fid_mat, fid_dli_curves, fid_pools=get_dli_features_dict(samples, p_data_analysis)
    cluster_parameters=get_cluster_parameters(samples, fid_dli_curves)
    pool_parameters=get_pool_parameters(fid_pools)
    cluster_group_dict=get_fclusterdata(cluster_parameters)
    plots_dict=plots.build_feature_plots(fid_mat, fid_dli_curves, fid_pools, sample_order, 
                                         result_path)
    summary_dict={'ident_res' : ident_dict,
                  'fcluster_res' : cluster_group_dict,
                  'plots_res' : plots_dict,
                  'fit_curve_res': cluster_parameters,
                  'pool_curve_res': pool_parameters}
    return summary_dict
    

def get_dli_features_dict(samples, parameters):
    overall=emzed.utils.mergeTables(samples, reference_table=samples[0])
    features=overall.splitBy('feature_id')
    tp=set(overall.time.values)
    num_tp=len(set(overall.time.values))
    time_range=(min(tp), max(tp))
    parameters['time_range']=time_range
    fid_mat=dict()
    fid_curves=dict()
    fid_pool=dict()
    for f in features:
        fid=f.feature_id.uniqueValue()
        if feature_fulfills_dli_criteria(f, parameters, float(len(samples))):
            fid_curves[fid]=build_dli_curve(f, parameters)
            fid_pool[fid]=build_metabolite_turnover_curve(f, parameters)
        fid_mat[fid]=build_mid_pattern(f, num_tp)
    return fid_mat, fid_curves, fid_pool


def feature_fulfills_dli_criteria(feature, parameters, no_samples):
    f=feature
    min_C13=parameters['min_labeling']
    feature_freq=parameters['feature_frequency']
    selection_crit1=(max(f.no_C13.values)>=min_C13 )
    selection_crit2=len(set(f.order.values))/no_samples>=feature_freq
    selection_crit3=check_s0(f, no_samples)
    if selection_crit1 and selection_crit2 and selection_crit3:
        return True


def check_s0(v, no_samples):
    # at leat 1 sample with lno_C13 >no_c13(s0)
    initial_c13=v.filter(v.time==v.time.min())
    initial_c13=initial_c13.no_C13.uniqueValue()
    pairs=set(zip(v.time.values, v.no_C13.values))
    # at leat 1 sample with lno_C13 >no_c13(s0)
    if initial_c13>0.05:
        return 
    check=len([p for p in pairs if p[1]>initial_c13])
    if float(check)/no_samples>0.3:
        return True    


def build_mid_pattern(feature, num_tp):
    """
    """
    f=feature
    times=sorted(list(set(f.time.values)))
    def fun (v, pos=times):
        return pos.index(v)
    f.addColumn('time_point', f.time.apply(fun))
    if f.num_c.countNone(): 
        value=np.zeros((1,num_tp))
    else:
        if f.num_c.uniqueValue()==0:
            value=np.zeros((1,num_tp))
        else:
            n_c=f.num_c.uniqueValue()+1
            value=np.zeros((n_c, num_tp))
            tuples=set(zip(f.num_isotopes.values, f.time_point.values, f.mi_frac_corr.values))
            
            for tup in tuples:
                value[tup[0]][tup[1]]=tup[2]
    f.dropColumns('time_point')
    return value   

def build_metabolite_turnover_curve(feature, parameters):
    time_range=parameters['time_range']
    f=feature
    tuples=set(zip(f.num_isotopes.values, f.time.values, f.mi_frac_corr.values))
    pairs=[v[1:] for v  in tuples if v[0]==0]
    pairs.sort(key= lambda v:v[0])
    time=[p[0] for p in pairs]
    fm0=[p[1] for p in pairs]
    y=[(max(fm0)-v + min(fm0)) for v  in fm0]
#    y=fm0
    fit_param=get_best_turnover_fit(time, y, time_range)
    print fit_param[5]
    fit_param=_adapt_y_fit(fit_param)
    measured=zip(time, fm0)
    return fit_param, measured


def get_best_turnover_fit(x,y,time_range):
    log_param=fitting_lgt(x,y,time_range)
    pt1_param=fitting_pt1(x,y,time_range)
    return _select_fit(pt1_param, log_param)    
    
    
def _select_fit(pt1_param, log_param):
    crit_pt1=[v!=None for v in pt1_param]
    crit_log=[v!=None for v in log_param]
    if all(crit_pt1):
        if all(crit_log):
            if log_param[4]>=pt1_param[4]:
                return pt1_param
            else:
                return log_param
        else:
            return pt1_param
    else:
        return log_param
    

def _adapt_y_fit(fit):
    if not None in fit:
        fm0_values=fit[1]
        max_fm0=fit[2] # k value of fit == max
        y=np.array([(max_fm0-v+min(fm0_values)) for v in fm0_values])
        fit=list(fit)
        fit1=[fit[0], y]
        fit1.extend(fit[2:])
        return tuple(fit1)
    
        

def build_dli_curve(feature, parameters):
    """
    """
    timepoints=feature.splitBy("time")
    time=[p.time.uniqueValue() for p in timepoints]
    no_C13=[p.no_C13.uniqueValue()for p in timepoints]
    max_C13=feature.max_num_c.uniqueValue()*2
    fit_param=get_best_fit(time, no_C13, max_C13, parameters)
    measured=zip(time, no_C13)
    return fit_param, measured

    
def get_best_fit(x, y, max_c, parameters):
    min_C13=parameters['min_labeling']
    max_dev=parameters['max_nrmse']
    time_range=parameters['time_range']
    log_param=fitting_lgt(x, y, time_range)
    pt1_param=fitting_pt1(x, y, time_range)
    if log_param[-2]>pt1_param[-2]:
       t_fit, c13_fit,no_C13, t50, nrmse, type_, _, _=pt1_param 
       if nrmse<max_dev and no_C13>min_C13 and (min_C13 <= max(c13_fit)<=3*max_c):
           return pt1_param
    else:
        t_fit, c13_fit, no_C13, t50, nrmse, type_, _, _=log_param 
        if nrmse<max_dev and no_C13>min_C13 and (min_C13 <=max (c13_fit)<=3*max_c):
           return log_param
    

def fitting_pt1(x, y, time_range):
     type_='pt1'
     def pt1(t,k,T):
        return k*(1-np.exp(-t/T))
     try:
         x, y, popt, perr=get_fitting_parameters(pt1, x, y, p0=(max(y), 60.0))
         k,T=popt
         k_var, T_var=perr
     except:
         return None, None, None, None, None, type_, None, None
     tr=time_range
     xn=np.linspace(tr[0], tr[1], 50)
     yn=pt1(xn,k,T)
     y_fit=pt1(np.array(x),k,T)
     # k might be completely overestimated therefore:
     t50=-T*np.log(0.5)
     t50_var=-T_var*np.log(0.5)
     nrmse=np.sqrt(np.mean([(y_fit[i]-y[i])**2 for i in range(len(y))]))/max(y_fit) 
     
     return xn, yn, float(k), float(t50), float(nrmse), type_, float(k_var), float(t50_var)

     
def fitting_lgt(x, y, time_range):
    type_='logistic'
    def logistic(t,T,k, y0):
        # source: http://en.wikipedia.org/wiki/Logistic_function
       return (k*y0*np.exp(t*T))/(k+y0*np.exp(t*T)-y0)
    try: 
        x, y, popt, perr=get_fitting_parameters(logistic, x, y, p0=(1e-5, max(y), min(y)))
        T_var, k_var, y0_var=perr
    except:
        return None, None, None, None, None, type_, None, None
    T,k, y0=popt
    tr=time_range
    xn=np.linspace(tr[0], tr[1], 50)
    yn=logistic(xn,T,k, y0)
    y_fit=logistic(np.array(x),T,k, y0)
    # by U Schmitt
    t50=np.log((k-y0)/y0)/T
    #by_pkiefer:
    t50_var=_calc_sigma(T, T_var, k, k_var, y0, y0_var)
    nrmse=np.sqrt(np.mean([(y_fit[i]-y[i])**2 for i in range(len(y))]))/max(y_fit)
    return xn, yn, float(k), float(t50), float(nrmse), type_, float(k_var), float(t50_var) 


def _calc_sigma(T, T_var, k, k_var, y0, y0_var):
    #first order taylor series approximation / gauss error propagation
    # source: http://de.wikipedia.org/wiki/Fehlerfortpflanzung
    dfdt = abs(-1*np.log(k/y0-1)/T**2*T_var)
    dfdk = abs(1/T*1/(y0*(k/y0-1))*k_var)
    dfdy0 = abs(-1/T*k/(k/y0-1)/y0**2*y0_var)
    return dfdt+dfdk+dfdy0


def _extract_fitting_dict(fid_curves):
    return {key: fid_curves[key][0][2:4] for key in fid_curves.keys() if fid_curves[key][0]}

        
def get_fitting_parameters(fun, x, y, p0, n=1):
    'fitts curve and removes up to n outliers'
    loops=0
    while True:
        print loops
        popt, pcov=curve_fit(fun, np.array(x), np.array(y), p0=p0)
        x,y,crit=remove_outlier(x,y,fun, popt)
        if not crit or loops>=n:
            break
        loops+=1
    perr = np.sqrt(np.diag(pcov)).tolist()
    return x,y, popt, perr
    
    
def remove_outlier(x,y, fun, popt, f=1.5):
    crit=False
    pos=range(len(x))
    exclude=None
    y_=[fun(v, *popt) for v in x]
    diff=[y[i]-y_[i] for i in pos]
#    upper = np.mean(diff) + f*np.std(diff)
    lower = np.mean(diff) - f*np.std(diff)
    #define outliers
    crit1=[i for i in pos if diff[i]<lower ]
    # values below close to not labeled
    if len(crit1):
        exclude=min(crit1)
        crit=True
    return [x[i] for i in pos if i != exclude], [y[i] for i in pos if i != exclude], crit
    

def get_cluster_parameters(samples, fid_curves):
    fid_num_c=_build_num_c_dict(samples)
    cluster_parameters=dict()
    for key in fid_curves.keys():
        if fid_curves[key][0]:
            v=fid_curves[key][0]
            k,t50, nrmse, type_, k_var, t50_var=v[2:]
            num_c=fid_num_c[key]
            k_rel=k/num_c
            if t50>0 and k_rel<2:
                value=(t50, k_rel, nrmse, type_, k_var, t50_var)
                cluster_parameters[key]=value
    return cluster_parameters


def _build_num_c_dict(samples):
    dictionary=dict()
    overview=emzed.utils.mergeTables(samples, reference_table=samples[0])
    pairs=set(zip(overview.feature_id.values, overview.num_c.values))
    for  key, value in pairs:
         dictionary[key]=value
    return dictionary

def get_pool_parameters(fid_pools):
    fid2fit=dict()
    for key in fid_pools.keys():
        if fid_pools[key][0]:
            v=fid_pools[key][0]
            fid2fit[key]=v[2:]
    return fid2fit
            
                                                   
    
def get_fclusterdata(clus_dict, t=1.5):
    keys=clus_dict.keys()
    pairs=np.array([clus_dict[key][:2] for key in keys])
    keys=[key for key in keys]
    # normalize values to get same weight of euclidian distance on each axis
    pairs -= np.mean(pairs, axis=0)
    pairs /= np.std(pairs, axis=0)
    try:
        clusters=cluster.hierarchy.fclusterdata(pairs, t, criterion='distance', metric='euclidean', 
                                                   depth=2, method='complete', R=None)
        return {key:value for key, value in zip(keys, list(clusters))}
    except:
        return {key: None for key in keys}
