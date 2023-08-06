# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:14:50 2014

@author: pkiefer
"""
import numpy as np

def labeling_dict_to_array(hm):
    n_rows = len(hm)
    n_cols = len(hm.values()[0])
    matrix = np.ndarray((n_rows, n_cols), dtype=float)
    for row, (fid, data) in enumerate(hm.items()):
        data.sort()
        for col, (time, value) in enumerate(data):
            matrix[row, col] = value
    row_maxima = np.nanmax(matrix, axis=1)
    perm = np.argsort(-row_maxima)
    matrix = matrix[perm]
    row_maxima = np.nanmax(matrix, axis=1)
    row_maxima = np.nanmax(matrix, axis=1)
    limits = np.arange(0.0, 1.01, .1)
    collected = []
    for low, high in zip(limits, limits[1:]):
        subm = matrix[(low <= row_maxima) & (row_maxima < high)]
        t_max_hs = []
        for row in subm:
            max_h = np.nanmax(row) / 2.0
            t_max_h = np.nanargmin(np.abs(row - max_h))
            t_max_hs.append(t_max_h)
        perm = np.argsort(t_max_hs)
        subm = subm[perm]
        collected.insert(0, subm)
    matrix = np.vstack(collected)
    return matrix
    
    
def build_plot(hm):
    arr = labeling_dict_to_array(hm)
    rows, cols = arr.shape
    print cols, rows
    pylab.figure(figsize=(15, 50))
    xlabel=['0s', '5s', '10s', '20s', '30s', '60s', '120s', '300s', '600s']
    plot_heatmap(arr, xlabel, ["-"] * rows)
#    plot_heatmap(arr, xlabel * cols, ylabel * rows)
#    plot_heatmap(arr, [''] * cols, [""] * rows)
    pylab.show()


import pylab
import matplotlib
import os

def plot_heatmap(data, xlabels, ylabels, label_right=False, colorbar= True, pad_colorbar=0.1, binsize=None,
                 title=None, save_path=None, cmap="hot", none_color="#777777"):
    """
    plots heatmap including axis labels, colorbar and title

    paramters:
      data        :  2d numpy array
      xlabels     :  list of strings, len is number of colums in data
      ylabels     :  list of strings, len is number of rows in data
      label_right :  boolean, indicates if labels at right of heatmap should be plotted
      colorbar    :  show colorbar, default = True
      pad_colorbar:  float in range 0 .. 1, distance of colorbar to heatmap
      binsize     :  None or float in range 0..1, if this value is not None the heat map and
                     the colorbar are discretised according to this value.
      title       :  None or string
      cmap        :  string with name of colormap, see help(pylab.colormaps) for alternatives
      none_color  :  rgb string for plotting missing values.
    """
    n_rows, n_cols = data.shape
    print n_rows, n_cols
    assert len(xlabels) == n_cols
    assert len(ylabels) == n_rows
    data = np.ma.masked_where(np.isnan(data), data)
    cmap = pylab.cm.get_cmap(cmap)
    cmap.set_bad(none_color)
    if binsize is not None:
        bounds = np.arange(-0.1, 1.001, binsize)
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    else:
        norm = None
    im = pylab.imshow(data, interpolation='none', cmap=cmap, norm=norm, aspect="auto")
    pylab.tick_params(axis="both", 
                      left="off", bottom="off", top="off", right="off",
                      labelbottom="on", labeltop="off", labelleft="on",
                      labelright="on" if label_right else "off")
    if colorbar:                      
        pylab.colorbar(im, pad=pad_colorbar, shrink=0.9)
    axes = im.get_axes()
    axes.set_xticks(range(n_cols))
    axes.set_xticklabels(xlabels, fontsize='small')
    axes.set_yticks(range(n_rows))
    axes.set_yticklabels(ylabels, fontsize='small')
    im.set_axes(axes)
    if save_path is not None:
        assert os.path.isdir(save_path), 'selected path %s is not a directory' %save_path
        pylab.savefig(os.path.join(save_path , title+".png"))

    
def plot_dli_curve(curves, x_ax_label, y_ax_label, xticks, unit,
                   yticks=None, ylabel=None):
    """
    """
    param, measured = curves
    x =[ v[0] for v in measured]
    y =[ v[1] for v in measured]
    try:
        t_fit, c13_fit=param[:2]    
    except:
        print param
        t_fit, c13_fit=(0,0)
    pylab.plot(t_fit, c13_fit, 'r', linewidth=3)
    pylab.xlabel("time " +unit, fontsize=14)
    if not ylabel:
        pylab.ylabel("labeled C", fontsize=14)
    else:
        pylab.ylabel(ylabel, fontsize=14)
    pylab.plot(x, y, "bo", markersize=11)
    axes=pylab.gca()
    # to suppress label
    #axes.set_xticks([])
    axes.set_xticks(xticks)
    axes.set_xticklabels(x_ax_label, fontsize='small')
    if  yticks:
        axes.set_yticks(yticks)
    else:
        axes.set_yticks(range(len(y_ax_label)))
    axes.set_yticklabels(y_ax_label, fontsize='small')
    axes.set_axes([axes])

