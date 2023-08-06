# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:18:50 2014

@author: pkiefer
"""
import emzed
import hires
import helper_funs as helper
import objects_check as checks


def process_peakmaps(peakmaps, processing, alignment, calib_table):
    """ loading all peakmaps from directory path. if ignore_blanks==True all peakmaps containing
        label '_blank' in file name are ignored. In case of FTMS data sets (e.g. Orbitrap) 
        artefacts peaks originating to gauss centroid transformation are remove if remove_shoulders
        is True
    """
    remove=processing['remove_shoulder']
    if remove:
            peakmaps=remove_shoulders(peakmaps)
    if not alignment['mz_calib_table']:
        print 'mz calibration table is missing: no mass alignment performed!'
        return peakmaps
    return mz_align_peakmaps(peakmaps, calib_table, alignment)
        

def remove_shoulders(peakmaps):
    [hires.cleanup_peakmap(pm) for pm in peakmaps]
    [helper.label_peakmap_processing(pm, 'shoulder removed') for pm in peakmaps]
    return peakmaps

    
def mz_align_peakmaps(peakmaps, calib_table, alignment, path=None):
    """
    """
    a=alignment
    tables=[pm2calib_table(calib_table, pm, mztol=a['mztol']) for pm in peakmaps]
    aligned=[]
    if alignment['mz_alignment']:
        for t in tables:
            print "mass aligning peakmap %s ..." %t.source.uniqueValue()
            t=emzed.align.mzAlign(t, calib_table, tol=a['mztol'], minR2=a['minR2'], 
                                  interactive=a['interactive'], destination=path)
        aligned.append(t)
        pms_aligned=[t.peakmap.uniqueValue() for t in aligned]
        [helper.label_peakmap_processing(pm, 'mass_aligned') for pm in pms_aligned]
    else:
        print 'NO MZ_ALIGNMENT'
        pms_aligned=[t.peakmap.uniqueValue() for t in tables]
    pms_aligned=[helper.peakmap_as_table(pm) for pm in pms_aligned]
    return pms_aligned


def pm2calib_table(calibration_table, peakmap, mztol=0.01):
    """ helper function for mass calibration. Peakmaps are added to mass calibration
        table and ms peaks are extracted by integration. 
    """
    t=calibration_table.copy()
    required=["mzmin", 'mzmax', "rtmin","rtmax"]
    checks.table_has_colnames(required, t)
    supportedPostfixes=t.supportedPostfixes(required)
    for pstfx in supportedPostfixes:
         t.updateColumn("peakmap"+pstfx, peakmap)
    t=emzed.utils.integrate(t, 'emg_exact', n_cpus=1)
    for pstfx in supportedPostfixes:
         # update format of rtmin and rtmax
         t.updateColumn("rtmin"+pstfx, t.getColumn("rtmin"+pstfx),
                              format_="'%.2fm' %(o/60.0)"+t.title)
         t.updateColumn("rtmax"+pstfx, t.getColumn("rtmax"+pstfx),
                              format_="'%.2fm' %(o/60.0)")
         t.updateColumn('rt'+pstfx, t.getColumn("params"+pstfx).apply(lambda v: v[1]))
         t.addColumn("source"+pstfx, peakmap.meta.values()[0])
    t.updateColumn("polarity", peakmap.polarity)
    emzed.utils.recalculateMzPeaks(t)
    return t


def _add_mzminmax(t, mztol):
    t.updateColumn('mzmin', t.mz_hypot-mztol)
    t.updateColumn('mzmax', t.mz_hypot+mztol)
    
        
