# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 22:20:36 2020

Edits flexicon.csv
Makes sure any cited from Epps/Ob fieldnotes is ordered as the headword of
any related entries, and not the variant.

Also migrates any bibliographic variant up to the highest-level headword.

@author: marks
"""

import pandas as pd
from ast import literal_eval
from AddIPAFlex import to_ipa

in_file = 'flexicon.csv'
out_file = 'flexiconNEW.csv'

bibs = ('sil dict 2011', 'barbosa', 'martins', 'weir', 'cartilhas')

# decorator
def null_as_dict(f):
    def g(x, *args, **kwargs):
        if x:
            return f(x, *args, **kwargs)
        else:
            return f({}, *args, **kwargs)
    return g

def main():
    global flexicon, hypoth_entries
    flexicon = pd.read_csv(in_file, index_col='entry_id', keep_default_na=False)
    literal_eval_dfs(flexicon)
    replace_na(flexicon, 'variant_of', dict)
    hypoth_entries = pd.DataFrame(columns=flexicon.columns)
    
    print(len(flexicon))
    headwords = [x for x in flexicon['variant_of']]
    headwords = headwords.count(False)
    
    
    flexicopy = flexicon.copy()
    for index, row in flexicopy.iterrows():
        flatten_entry(index, row)
        
        if 'epps' not in row['bibliography'].lower() and not row['variant_of']:
            add_hypoth_entry(index, row)
            
    for index, row in hypoth_entries.iterrows():
        # {index: {'type':'_component-lexeme', 'variant-type': bib}}
        var_index = row['these_vars']
        var_vars = flexicon.at[var_index, 'these_vars']
        var_bib = flexicon.at[var_index, 'bibliography']
        
        these_vars = get_biblio_vars(var_vars)
            
        # update variant_of for all these_vars
        update_var_of(these_vars, var_index, index)
    
        these_vars[var_index] = {'type':'_component-lexeme',\
                  'variant-type': var_bib}
        row['these_vars'] = these_vars
        
        # add row to flexicon
        flexicon.loc[index] = row
        
        # update these_vars in original row
        flexicon.at[var_index, 'these_vars'] = var_vars
        
    print(len(flexicon))
    flexicon.to_csv(out_file)
    
    final_headwords = [x for x in flexicon['variant_of']]
    final_headwords = final_headwords.count(False)
    print(final_headwords-headwords)
    
def add_hypoth_entry(index, row):
    bib = get_bib(row['bibliography'])
    new_id = new_unique_id(index)
    new_headword = to_ipa( row['headword'], bib=bib )
    assert new_headword
    new_id = new_headword + '_' + new_id
    
    flexicon.at[index, 'variant_of'][new_id] = {'type':'_component-lexeme',
                  'variant-type': bib}
    
    new_data = row.copy()
    new_data['these_vars'] = index
    new_data['variant_of'] = {}
    new_data['headword'] = new_headword
    new_data['pronunciation'] = new_headword
    new_data['note'] = {'Note': f'Predicted phonemic form from source {bib}.'}
    
    hypoth_entries.loc[new_id] = new_data

@null_as_dict   
def get_biblio_vars(vars):
    out = {}
    for k, v in vars.copy().items():
        if 'variant-type' not in v:
            continue
        v_type = str( v['variant-type'] ).lower()
        assert 'epps' not in v_type
        if v_type in bibs:
            out[k] = vars.pop(k)
    return out

def update_var_of(vars, old_id, new_id):
    for v_id, v_dict in vars.items():
        v_var_of = flexicon.at[v_id, 'variant_of']
        assert old_id in v_var_of
        v_var_of[new_id] = v_var_of.pop(old_id)
        flexicon.at[v_id, 'variant_of'] = v_var_of
    
def flatten_entry(eid, row):
    these_vars = row['these_vars']
    if not these_vars:
        return
    
    for vid in these_vars.copy().keys():
        v_row = flexicon.loc[vid]
        v_vars = v_row['these_vars']
        if not v_vars:
            continue
        for v_v_id, v_v_data in v_vars.copy().items():
            v_v_these_vars = flexicon.at[v_v_id, 'these_vars']
            if v_v_these_vars:
                flatten_entry(v_v_id, flexicon.loc(v_v_id))
            v_v_type = v_v_data['variant-type'].lower()
            assert 'epps' not in v_v_type and 'obert' not in v_v_type
            if v_v_type in bibs:
                move_variant(vid, eid, v_v_id)
    
def move_variant(source, target, var_id):
    #print('called it')
    # pop variant from source row
    source_vars = flexicon.at[source, 'these_vars']
    var = source_vars.pop(var_id)
    flexicon.at[source, 'these_vars'] = source_vars
    
    # add to target row
    flexicon.at[target, 'these_vars'][var_id] = var
    
    # update variant_of
    var_of = flexicon.at[var_id, 'variant_of']
    this_var_of = var_of.pop(source)
    var_of[target] = this_var_of
    flexicon.at[var_id, 'variant_of'] = var_of
    
def new_unique_id(eid):
    guids = list(flexicon.index) + list(hypoth_entries.index)
    guids = [x.split(sep='_')[1] for x in guids]
    
    # generate unique id by manipulating last chunk of given id
    unique_chunk = eid.split(sep='-')[-1]
    chunk_val = int(unique_chunk, 16)
    
    this_guid = eid.split(sep='_')[1]
    back_step = 16
    i = 0
    while this_guid in guids:
        chunk_val += 1
        i += 1
        tmp = hex(chunk_val)[2:]
        tmp = '-'.join(this_guid.split(sep='-')[:-1] ) + tmp
        if i > 1000:
            assert False, tmp
        elif len(tmp) > len(this_guid):
            chunk_val -= back_step
            back_step *= 2
        elif tmp not in guids:
            return tmp
        
def get_bib(bib, epps_ob=False):
    bib = bib.lower()
    if "weir" in bib:
        return "Weir"
    
    elif "martins" in bib:
        return "Martins"
    
    elif "barbosa" in bib:
        return "Barbosa"
    
    elif "sil" in bib:
        return "Sil Dict 2011"
    
    elif "cartilha" in bib or 'liç' in bib:
        return "Cartilhas"
    
    elif not bib:
        return 'undef'
    
    elif epps_ob and 'epps' in bib:
        return 'Fieldnotes Epps/Obert; 2018'
    
    else:
        assert False, bib
    
def literal_eval_dfs(df):
    literal_eval_col(df, 'variant_of')
    literal_eval_col(df, 'note')
    literal_eval_col(df, 'sense')
    literal_eval_col(df, 'these_vars')
    
def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None\
               for row in df[col]]

# new_na is callable and returns a value
def replace_na(df, col, new_na):
    df.at[:, col] = [x if x else new_na() for x in df[col]]

if __name__ == '__main__':
    main()