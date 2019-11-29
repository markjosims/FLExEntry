# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 21:38:32 2019

@author: Mark
"""

import json
import os
import glob

def generate_lex_dir(df1, df2):
    clean_dir('/entries/.*')
    global variants, senses_df
    entries_df = df1
    senses_df = df2
    # indices of entries that aren't variants
    headwords = [not x for x in entries_df['variant'] ]
    # all entries that are variables
    variants  = [not x for x in headwords]

    headwords = entries_df[headwords]
    variants  = entries_df[variants]
    assert len(headwords) + len(variants) == len(entries_df)
    headwords.reset_index(inplace=True)
    variants.reset_index(inplace=True)
    del entries_df
    
    
    entry_ids = headwords['entry_id']
    vars_to_hdwrds = [get_headword_id(row) for row in variants.iterrows()]
    var_ids = variants['entry_id']
    
    vars_to_hdwrds = [x for x in vars_to_hdwrds if x] # remove blank strings from list    
     
    # change variant col to be list of variant ids
    for index, row in headwords.iterrows():
        this_id = row['entry_id']
        # all indices of variants whose headword ids point to this entry
        # as listed in vars_to_hdwrds
        var_idx = [i for i, h_id_list in enumerate(vars_to_hdwrds) if\
                   any(h_id == this_id for h_id in h_id_list)]
        # entry ids of variants themselves
        these_vars = [var_ids[i] for i in var_idx]
        # change val of variant column to these variant ids
        # (was empty before)
        row['variant'] = these_vars
        
    
    # add new col for variants of variants
    # boolean vector, True if variant at index has other variants pointing to it
    super_variants = [any(var_id in these_ids for these_ids in vars_to_hdwrds)\
                      for var_id in var_ids]
    # variant ids for these sub-variants (if any)
    vars_of_vars = []
    for has_sub_var, row in zip(super_variants, variants.iterrows()):
        if not has_sub_var:
            # skip if no variants of this varaint
            vars_of_vars.append([])
            continue
        index, row = row[0], row[1]
        this_id = row['entry_id']
        # all indices of variants pointing to this entry as listed in vars_to_hdwrds
        var_idx = [i for i, h_id_list in enumerate(vars_to_hdwrds) if\
                   any(h_id == this_id for h_id in h_id_list)]
        # entry ids of variants themselves
        these_vars = [var_ids[i] for i in var_idx]
        vars_of_vars.append(these_vars)
    # create new column for sub variants
    variants.loc[:,'var_of_var'] = {i:vov for i, vov in enumerate(vars_of_vars)}
    
    # add a new col for variants of senses
    sense_vars = []
    for index, row in senses_df.iterrows():
        this_id = row['sense_id']
        # all indices of variants pointing to this sense as listed in vars_to_hdwrds
        var_idx = [i for i, h_id_list in enumerate(vars_to_hdwrds) if\
                   any(h_id == this_id for h_id in h_id_list)]
        # entry ids of variants themselves
        these_vars = [var_ids[i] for i in var_idx]
        sense_vars.append(these_vars)
    senses_df['var_of_sense'] = sense_vars
    
    del entry_ids, vars_to_hdwrds, var_ids
    
    # dump to json
    temp = 'temp.json'
    for index, row in headwords.iterrows():
        # we want to create a json file for each headword
        data = dict(row)
        data.pop('index')
        data['variant'] = fetch_all_vars( data['variant'] )
        data['sense'] = fetch_all_senses( data['sense'] )
        filehead = data['headword'].replace('/', '_')
        filehead = filehead.replace(' ', '_')
        filehead = filehead.replace('?', '')
        filename = 'entries/' + filehead + '.json'
        with open(temp, 'w') as f:
            # create temp json file
            json.dump(data, f, indent=2)
        with open(filename, 'w', encoding='utf8') as f:
            with open(temp, 'rb') as t:
                for line in t:
                    # fix escaped unicode sequences
                    line = line.decode('unicode_escape')
                    # remove extra carriage return
                    line = line.replace('\r', '')
                    
                    f.write(line)
            
def clean_dir(folder):
    files = glob.glob(folder)
    for f in files:
        os.remove(f)


def fetch_all_vars(all_vars):
    if not all_vars:
        return None
    elif type(all_vars[0]) == dict():
        return all_vars
    else:
        return [fetch_var(var) for var in all_vars]

def fetch_var(var):
    global variants
    row = list(variants['entry_id']==var)
    assert row.count(True) == 1, var
    idx = row.index(True)
    row = variants.loc[idx]
    var_of_var = row['var_of_var']
    if var_of_var and type(var_of_var[0]) != dict():
        variants.loc[idx,'var_of_var'] = [fetch_var(vov) for vov in var_of_var]
    sense = row['sense']
    if type(sense[0]) != dict():
        row['sense'] = fetch_all_senses(sense)
    out = dict(row)
    #print(out)
    #out.pop('index')
    return out
    
def fetch_all_senses(all_senses):
    if not all_senses:
        return None
    elif type(all_senses[0]) == dict():
        return all_senses
    else:
        return [fetch_sense(sense) for sense in all_senses if sense != '[]']

def fetch_sense(sense):
    global senses_df, variants
    row = list(senses_df['sense_id']==sense)
    assert row.count(True) == 1, sense + str(type(sense))
    idx = row.index(True)
    row = senses_df.loc[idx]
    var_of_sense = row['var_of_sense']
    if var_of_sense and type(var_of_sense[0]) != dict():
        row['var_of_sense'] = [fetch_var(vos) for vos in var_of_sense]
    out = dict(row)
    #print(out)
    #out.pop('index')
    return out
    
    
def get_headword_id(variant):
    if type(variant) is tuple:
        return [variant[0]]
    assert type(variant) is list, variant
    return [x[0] for x in variant]