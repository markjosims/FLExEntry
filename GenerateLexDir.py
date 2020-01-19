# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 21:38:32 2019

@author: Mark
"""

import json
import os
import pandas as pd
from shutil import rmtree
from ast import literal_eval
from time import time

master = 'flexicon.csv'
senses = 'flex_senses.csv'
out = 'entries'

# decorator
def time_exec(f):
    def g(*args, **kwargs):
        start = time()
        f(*args, **kwargs)
        end = time()
        (str(f), end-start)
    return g

def main():
    flex_df = pd.read_csv('flexicon.csv', keep_default_na=False)
    senses =  pd.read_csv('flex_senses.csv', keep_default_na=False)
    
    flex_df, senses = literal_eval_dfs(flex_df, senses)
    
    generate_lex_dir(flex_df, senses)
    
def literal_eval_dfs(flex_df, senses):
    literal_eval_col(flex_df, 'variant_of')
    literal_eval_col(flex_df, 'note')
    literal_eval_col(flex_df, 'sense')
    literal_eval_col(flex_df, 'these_vars')
    literal_eval_col(senses, 'gloss')
    literal_eval_col(senses, 'def')
    
    return flex_df, senses
    

def generate_lex_dir(entries_df, senses_df):
    clean_dir(out)
    # indices of entries that aren't variants
    headwords = [not x for x in entries_df['variant_of'] ]
    # all entries that are variables
    variants  = [not x for x in headwords]
    
    # create separate dataframes for entries that are variants and that aren't
    headwords = entries_df[headwords]
    variants  = entries_df[variants]
    assert len(headwords) + len(variants) == len(entries_df)
    
    # reset indices
    headwords.reset_index(inplace=True)
    variants.reset_index(inplace=True)
    
    # original df not needed
    del entries_df
    
    # re-populate senses col for headwords and variants
    # result is dictionary, k is id of sense, v is sense data
    senses_col(variants, senses_df)
    senses_col(headwords, senses_df)
    
    # populate these_vars col for each df
    # result is dictionary, k is id of variant, v is variant type
    sense_vars_col(senses_df, variants)
    vars_of_vars_col(variants)
    entry_vars_col(headwords, variants)

    # write to json
    write_json_dir(headwords)

@time_exec
def sense_vars_col(senses_df, variants):
    for index, row in senses_df.copy().iterrows():
        sense_id = row['sense_id']
        these_vars = row['these_vars']
        get_vars_from_id(sense_id, these_vars, senses_df, variants)

@time_exec
def vars_of_vars_col(variants):
    for index, row in variants.copy().iterrows():
        var_id = row['entry_id']
        these_vars = row['these_vars']
        get_vars_from_id(var_id, these_vars, variants, variants)
    
@time_exec
def entry_vars_col(headwords, variants):
    for index, row in headwords.copy().iterrows():
        entry_id = row['entry_id']
        these_vars = row['these_vars']
        get_vars_from_id(entry_id, these_vars, headwords, variants)
        
@time_exec     
def senses_col(parent_df, senses_df):
    for index, row in parent_df.copy().iterrows():
        entry_id = row['entry_id']
        these_senses = row['sense']
        get_senses_from_id(entry_id, these_senses, parent_df, senses_df)

# given an entry id corresponding to a row in parent_df
# set row, these_vars to dicts containing data for all variants
# pointing to row as head
def get_vars_from_id(entry_id, these_vars, parent_df, variants):
    if not these_vars:
        return
    
    if 'entry_id' in parent_df.columns:
        id_col = 'entry_id'
    else:
        assert 'sense_id' in parent_df.columns
        id_col = 'sense_id'
    # assert entry_id in list(parent_df[id_col]), entry_id
    
    # dict of dicts, appended from rows of variants df
    out = {}
    
    has_var = variants[[bool(var_id) and var_id in these_vars for var_id in variants['entry_id']]]
    
    for index, row in has_var.iterrows():   
        var_id = row['entry_id']
        assert entry_id != var_id
        
        var_data = dict(row)
        # get datum for type of variant
        var_data['var_type'] = var_data['variant_of'][entry_id]
        
        # call recursively if variant might itself have variants
        if var_data['these_vars'] and all(type(x) is str for x in var_data['these_vars'].values()):
            get_vars_from_id(var_data['entry_id'], var_data['these_vars'], variants, variants)        
        var_data.pop('variant_of')
        var_data.pop('index')     
        var_data.pop('entry_id')
        out[var_id] = var_data
    index = parent_df.loc[lambda df : df[id_col] == entry_id].index[0]
    parent_df.at[index, 'these_vars'] = out
    
def get_senses_from_id(entry_id, these_senses, parent_df, senses_df):    
    if not these_senses:
        return
    has_sense = senses_df[[bool(row_id) and row_id in these_senses for row_id in senses_df['sense_id']]]
    out = {}
    
    for index, row in has_sense.iterrows():
        sense_id = row['sense_id']
        data = dict(row)
        data.pop('sense_id')
        out[sense_id] = data
    
    index = parent_df.loc[lambda df : df['entry_id'] == entry_id].index[0]
    parent_df.at[index, 'sense'] = out

# creates a json file for each headword
@time_exec
def write_json_dir(headwords):
    for index, row in headwords.iterrows():
        data = dict(row)
        data.pop('index')
        filehead = data['entry_id']
        filehead = rep_all(filehead, '/ ', '_')
        filehead = rep_all(filehead, '()[]? ', '')
        filename = out + '\\' + filehead + '.json'
        temp = json.dumps(data, indent=2)
        temp = temp.encode('utf8')
        with open(filename, 'w', encoding='utf8') as f:
            temp = temp.decode('unicode_escape')
            f.write(temp)
            
def clean_dir(folder):
    wd = os.getcwd()
    folder_path = wd+'\\'+folder
    try:
        rmtree(folder_path)
    except FileNotFoundError:
        pass
    os.mkdir(folder_path)

        
def rep_all(s, chars, tgt):        
    for c in chars:
        s = s.replace(c, tgt)
    return s

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None\
               for row in df[col]]

if __name__ == '__main__':
    main()