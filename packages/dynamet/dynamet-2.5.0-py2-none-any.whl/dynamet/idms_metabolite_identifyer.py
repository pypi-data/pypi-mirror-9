# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 14:29:23 2013

@author: pkiefer



"""
import emzed
import numpy as np
import re
import os
MMU=0.001
import objects_check as checks
import helper_funs as helper


def identify_metabolites(tables, parameters=None):
    summary=_build_overall_met_para_table(tables)
    selected=_filter_for_min_quality(summary)
    selected=identify_with_db(selected, parameters=parameters)
    selected=_build_dict_from_results(selected)
    return selected


def _build_overall_met_para_table(tables):
    overall=emzed.utils.mergeTables(tables, reference_table=tables[0])
    _add_polarity(overall)
    overall.getColNames()
    selected=['adduct_group', 'polarity', 'possible_adducts', 'feature_id', 'rt', 
              'adduct_mass_shift', 'possible_m0', 'mz0', 'z', 'num_c', 'min_num_c', 
              'max_num_c', 'q_score', 'origin_of_c_estimation']
    types=[int, str, str, int, float, float, float, float, int, int, int, int, int, str]
    overall=overall.extractColumns(*selected)
    features=overall.splitBy('feature_id')
    ident=[]
    for f in features:
        reduced=emzed.utils.toTable('adduct_group', tuple([f.adduct_group.uniqueNotNone()]))
        for colname, type_ in zip(selected[1:],types[1:]):
            values=f.getColumn(colname).values
            if len(set(values))==1:
                reduced.addConstantColumn(colname, f.getColumn(colname).uniqueValue(), type_=type_)
            else:
                check = all([((isinstance(v, float)) | (isinstance(v, float)))\
                            for v in values])
                if check:
                    value=np.mean(values)
                    reduced.addColumn(colname, value, type_=type_)
                else:
                    reduced.addColumn(colname, None, type_=type_)
        ident.append(reduced)
    return emzed.utils.mergeTables(ident, force_merge=True)


def _add_polarity(t):
    def fun(pm):
        return pm.polarity
    t.addColumn('polarity', t.peakmap.apply(fun), type_=str)
    

def _filter_for_min_quality(t):
    required=['q_score', 'num_c']
    checks.table_has_colnames(required, t)
    return t.filter((t.q_score>0) & (t.num_c>=1))
 
 
def identify_with_db(reduced, parameters=None):
    """
    """
    if not parameters:
        mztol=3*MMU
        kegg=build_db()
    else:
        mztol = parameters['isol_width']
        kegg=build_db(parameters['data_base'])
    def num_c(v, el='C'):
        return count_element(el, v)
    def fun(value, mztol=mztol):
        return any([v<mztol for v in value])
    kegg=reduce_db_size(reduced, kegg)
    with_m0=reduced.filter(reduced.possible_m0.apply(any)==True)
    r=reduced.filter(reduced.possible_m0.apply(any)==False) 
    wm=_cand_by_m0(with_m0, kegg)
    wm=wm.filter(wm.mf__0.apply(num_c).inRange(wm.min_num_c, wm.max_num_c))
    r=r.leftJoin(kegg, r.mz0.approxEqual(kegg.mz0, mztol) & (r.z==kegg.z) & \
                (r.polarity == kegg.polarity))
    remaining=r.filter(r.mf__0.apply(num_c).inRange(r.min_num_c, r.max_num_c))
    identified=emzed.utils.mergeTables([wm, remaining])
    i=identified
    identified.addColumn('delta_mz_ppm', (i.mz0-i.mz0__0)/i.mz0__0 *1e6, format_='%.1f')
    return identified


def reduce_db_size(t, db):
    """ takes into account polarity. if all EIC peaks in table have same polarity
        all entrys in db with opposit polarity are removed
    """
    try:
        polarity=t.polarity.uniqueValue()
        return db.filter(db.polarity==polarity)
    except:
        return db
        
#########################################################################
def _cand_by_m0(t, db, mztol=3*emzed.MMU):
    """
    """
    t_=_expand_table(t)
    result=t_.leftJoin(db, t_.m0.approxEqual(db.m0, mztol)\
            & (db.adduct_name == t_.adduct_name))
    
    result.dropColumns('m0')
    return result
#########################################################################
def _expand_table(t):
    features=t.splitBy('feature_id')
    subsets=[]
    for f in features:
        assert len(set(f.possible_m0.values))==1 
        try:
            pairs=zip(f.possible_m0.uniqueValue(), f.possible_adducts.uniqueValue() )
            masses=emzed.utils.toTable('m0', [v[0] for v in pairs])
            masses.addColumn('adduct_name', [v[1] for v in pairs])
        except:
            print f.possible_m0.values
            assert False
        subset=f.join(masses, True)
        subset.removePostfixes()
        subsets.append(subset)
    return emzed.utils.mergeTables(subsets)
    
#################################################################################
# building data base for metabolite identification    
    
def build_db(data_base='kegg'):
    pc=load_internal_db(key=data_base)
    if not pc:
        if os.path.isfile(data_base):
            pc=helper.load_table_items(data_base)
        else:
            helper.load_table_items(get_external_data_base())
    db=pc.filter(pc.mf.containsOnlyElements(['C','H', 'N', 'O', 'P', 'S']))
    if db.hasColumn('synonnyms'):
        db.renameColumns(synonyms = 'compound_names')
    remove=('is_in_kegg', 'is_in_hmdb', 'z_signed', 'iupac')
    has=db.hasColumn
    rem=db.dropColumns
    [rem(col) for col in remove if has(col)] 
    adducte=build_adduct_table()
    db=db.join(adducte, True)
    db.removePostfixes()
    db.addColumn("mz0", (db.m0+db.mass_shift)/db.z, type_=float,
                   format_="%.5f")
    if db.hasColumn('url'):
        db.setColFormat('url', '%s')
    return db

def get_external_data_base(path=None):
    path=emzed.gui.DialogBuilder('CHOOSE EXTERNAL DATA BASE')\
    .addFileOpen('select_db',  basedir=path, formats=['table', 'csv'], 
                 help='accepeted formats are table and'\
                ' csv. Required Column names are `m0: monoisotopic mass` and'\
                ' `mf: molecular fomulas`.')\
    .show()
    db=helper.load_table_items(path)
    _check(db)
    return path


def _check(db):
    required=['m0', 'mf']
    checks.table_has_colnames(required, db)
    assert db.getColType('m0') == float, 'm0 must be float values. data base is not valid'

    
def load_internal_db(key='kegg'):
    db_dic={'kegg' : emzed.db.load_kegg,
     'pubchem' : emzed.db.load_pubchem,
     'hmdb' : emzed.db.load_hmdb}
    if db_dic.has_key(key):
        return db_dic[key]()

     
def build_adduct_table():
    adducte=emzed.adducts.all.toTable()
    adducte=helper.add_observed_adducts(adducte)
    def fun(v):
        if v < 0:
            return '-'
        return '+'
    adducte.addColumn('polarity', adducte.z_signed.apply(fun))
    return adducte 

     
def count_element(el, mf):
    """Alphabetic order of elements in MF: 
    """
    def num2str(v):
        if v=='':
            return 1
        else:
            return int(v) 
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    selected=[num2str(number) for element, number in fields if element==el]
    return int(sum(selected))    


def _build_dict_from_results(table):
    t=table.collapse('feature_id')
    pairs=zip(t.feature_id.values, t.collapsed.values)
    ident_dict=dict()
    for fid, tab in pairs:
        ident_dict[fid]=tab
    return ident_dict


def correct_synonyms(t):
    def fun(v):
        return v.replace(';', ',')
    
    t.replaceColumn('compound_names__0', t.compound_names__0.apply(fun))
    
    