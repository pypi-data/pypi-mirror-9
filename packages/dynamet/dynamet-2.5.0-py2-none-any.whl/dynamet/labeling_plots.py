# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:58:35 2014

@author: pkiefer
"""
import emzed
import numpy as np
import dict_to_mat
import matplotlib.pyplot as plt
import matplotlib
import os



def build_feature_plots(fid_mat, fid_curves, fid_pools, sample_order, result_path):
    label_plots=dict()
    pool_plots=dict()
    keys=set(fid_mat.keys()).intersection(set(fid_curves.keys()))
    path=result_path
    for key in keys:
        # 1. labeling plot
        title='feature_id_'+str(key)
        plot_dli_hm_and_curves(fid_mat[key], fid_curves[key], sample_order, title=title, path=path)
        target=os.path.join(path, title+'.png')
        update_dict(label_plots, key, target)
        title=title+'_M0_dilution'
        plot_pool_exchange(fid_pools[key], sample_order, title=title, path=path)
        target=os.path.join(path, title+'.png')
        update_dict(pool_plots, key, target)
    return label_plots, pool_plots


def update_dict(fid2plot, key, target):
    if os.path.isfile(target):
            plot=emzed.io.loadBlob(target)
            fid2plot[key]=plot
    else:
        fid2plot[key]=None


def plot_dli_hm_and_curves(mat, curves, sample_order, title=None, path=None):
    if mat!=None:
        y, x = mat.shape
        plt.figure(figsize=(14,6))
        def fun(i, y=y):
                 fac=(np.floor(np.ceil(y/10.0)/2.0))*2
                 if not fac:
                     fac=1
                 if float(i)/fac==int(i/fac):
                     return str(i)
                 else:
                     return ''
        ylabel_hm=[]
        for i in range(y):
            if fun(i):
                ylabel_hm.append('M'+fun(i))
            else:
                ylabel_hm.append('')
        timepoints=sorted(list(set(sample_order['time'])))
        xlabel_hm=[str(v)+'s' for v  in timepoints]
        plt.subplot(122)
        dict_to_mat.plot_heatmap(mat, xlabel_hm, ylabel_hm, title=title, 
                                     save_path=path, colorbar=False)
        if curves!=None:
            max_x=max(sample_order['time'])
            step=np.ceil(max_x/5)
            # to suppress xlabel
            #xlabel=['']*x
            x_ax_label_dli, unit=smart_time_axis(max_x)
            xticks=[int(v) for v in np.arange(0,max_x+1, step)]
            y_=[int(np.ceil(v[1])) for v in curves[1]]
            y_=max(y_)+1
            y_ax_label_dli=[fun(i) for i in range(y_)]
            plt.subplot(121)
            if title:
                plt.title=title
            dict_to_mat.plot_dli_curve(curves, x_ax_label_dli, y_ax_label_dli, xticks, unit)    
#        plt.show()
        if path and title:
            target=os.path.join(path , title+".png")
            assert os.path.isdir(path), 'selected path %s is not a directory' %path
            plt.savefig(target)
        plt.close()    

def plot_pool_exchange(pools, sample_order, title=None, path=None):
    if pools != None:
        max_x=max(sample_order['time'])
        step=np.ceil(max_x/5)
        x_ax_label, unit=smart_time_axis(max_x)
        xticks=[int(v) for v in np.arange(0,max_x+1, step)]
        yticks=[float(v) for v in np.arange(0,1.3,0.2)]
        y_ax_label=[str(v) for v in np.arange(0,1.3,0.2)]
        plt.figure(figsize=(7,6))
        if title:
            plt.title=title
        dict_to_mat.plot_dli_curve(pools, x_ax_label, y_ax_label, xticks, unit, yticks=yticks,
                                   ylabel='M0 fraction') 
        if path and title:
            target=os.path.join(path , title+".png")
            assert os.path.isdir(path), 'selected path %s is not a directory' %path
            plt.savefig(target)
        plt.close()    

def smart_time_axis(tmax):
    step=np.ceil(tmax/5) 
    units=['[s]', '[min]', '[h]']
    conversion=[1, 60, 3600] # sec , min, h
    which=len([step/v for v in conversion if step/v>=1])-1 # units where step >1
    norm=conversion[which]
    x_labels=[str(int(v/norm)) for v in np.arange(0,tmax+1, step)]
    return x_labels, units[which]

    
def build_color_code():
    color_dict={1: (0,0,1),
                2: (0,0.8,0),
                3: (1,0,0),
                4: (0.4,0,0),
                5: (0.5,0.5,0),
                6: (0.2,1,0.7),
                7: (0.3,0.3,0.3),
                8: (0.7,0.2,0.4),
                9: (0.5,0.2,0),
                10: (0.5,0,0.2),
                11: (0.5,0.2,0.2),
                12: (0.2,0.2,0.5),
                13: (0.2,0.5,0.2),
                14: (0.5, 0.1, 0.5),
                15: (0.1,0.5,0.5),
                16: (0.5,0.1,0.5),
                17: (0.5,0.5,0),
                18: (0.1, 0.7, 0.3),
                19: (0.8, 0.5, 0.2),
                20: (0.8,0.2,0.5)}
    return color_dict


def plot_fcluster(fid_to_cluster_id, fid_to_curve_fitting, title, ax_limits=[None, None, -0.1, 1.1], 
                    path=None):
    """ plots cluster results with dictionaries fid_to_cluster_id[id] and fid_to_curve_fitting,
        you can set axis_limits [xmin, xmax, ymin, ymax], default =auto. 
    """
    font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 16}
    matplotlib.rc('font', **font)
    colors=set(fid_to_cluster_id.values())
    if len(colors)>20:
        assert  True, 'Too many clusters for colorcode'
    color_dict= build_color_code()
    plt.figure()
    for key in fid_to_cluster_id.keys():
        color_code=color_dict[fid_to_cluster_id[key]]
        plt.plot(fid_to_curve_fitting[key][0],fid_to_curve_fitting[key][1], 'o', color=color_code)
    if not all(ax_limits) == None:
        plt.axis(ax_limits)
    plt.xlabel(ur't$_{50}$ s', fontsize=18)
    plt.ylabel(ur'labeled fraction', fontsize=18)
#    plt.show()
    if path:
        target=os.path.join(path , title)
        assert os.path.isdir(path), 'selected path %s is not a directory' %path
        plt.savefig(target)
        plt.close()

   
def generate_fcluster_plot_from_result_file(res, path=None, title='feature_clustering_plot.png'):
    t=res.filter(res.fcluster_id.isNotNone())
    pairs=zip(t.feature_id.values, t.fcluster_id.values)
    fid2cluster_id={p[0]:p[1] for p in pairs}
    pairs=zip(t.feature_id.values, t.label_t50_sec.values, t.c13_fraction_calc.values)
    fid2curve_fit={p[0]:(p[1],p[2]) for p in pairs}
    t_max=get_tmax(t)
    print t_max
    plot_fcluster(fid2cluster_id, fid2curve_fit, title, path=path, ax_limits=[-1.0, None, -0.1, 1.1])
    if os.path.isdir(path):
        target=os.path.join(path, title)
        if os.path.isfile(target):
            return emzed.io.loadBlob(target)


def get_tmax(t, percentile=90):
    return np.percentile(t.label_t50_sec.values, percentile)

    
    
    

                                               
                                                   
    
    
    