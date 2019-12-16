# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 21:38:32 2019

@author: Mark
"""

import json
import os
import pandas as pd
from glob import glob 
from ast import literal_eval

def main():
    flex_df = pd.read_csv('flexicon.csv', keep_default_na=False)
    senses =  pd.read_csv('flex_senses.csv', keep_default_na=False)
    
    literal_eval_col(flex_df, 'variant')
    literal_eval_col(flex_df, 'note')
    literal_eval_col(flex_df, 'sense')
    literal_eval_col(senses, 'gloss')
    literal_eval_col(senses, 'def')
    
    generate_lex_dir(flex_df, senses)

def generate_lex_dir(df1, df2):
    clean_dir(r'\entries\*.json')
    global variants, senses_df, headwords
    entries_df = df1
    senses_df = df2
    # indices of entries that aren't variants
    headwords = [not x for x in entries_df['variant'] ]
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
    
    global entry_ids, var_ids, var_data
    # entry ids of headwords
    entry_ids = headwords['entry_id']
    
    # list of dicts, key is entry id of headword, val is type of variant
    var_data = variants['variant']
    
    # entry ids of variants
    var_ids = variants['entry_id']
   
    senses_df['these_vars'] = None
    variants['these_vars'] = None
    headwords['these_vars'] = None
    
    # populate these_vars col for each df
    # result should be dictionary, k is id of variant, v is variant type
    sense_vars_col(senses_df, variants)
    vars_of_vars_col(variants)
    entry_vars_col(headwords, variants)

    del entry_ids, var_ids, var_data
    write_json_dir()

def get_vars_from_id(entry_id, parent_df, variants):
    if 'entry_id' in parent_df.columns:
        id_col = 'entry_id'
    else:
        assert 'sense_id' in parent_df.columns
        id_col = 'sense_id'
    
    
    

# wcreates a json file for each headword
def write_json_dir():
    # dump to json
    temp = 'temp.json'
    for index, row in headwords.iterrows():
        data = dict(row)
        data.pop('index')
#        if data['variant']:
#            print(data['variant'])
#        else:
#            print(data)
        # replace value
        filehead = data['entry_id']
        filehead = rep_all(filehead, '/ ', '_')
        filehead = rep_all(filehead, '()[]? ', '')
        filename = 'entries/' + filehead + '.json'
        with open(temp, 'w') as f:
            # create temp json file
            json.dump(data, f, indent=2)
        with open(filename, 'w', encoding='utf8') as f, open(temp, 'rb') as t:
            for line in t:
                # fix escaped unicode sequences
                line = line.decode('unicode_escape')
                # remove extra carriage return
                line = line.replace('\r', '')
                
                f.write(line)
            
def clean_dir(folder):
    wd = os.getcwd()
    files = glob(wd+folder)
    for f in files:
        os.remove(f)
        
def rep_all(s, chars, tgt):
    for c in chars:
        s = s.replace(c, tgt)
    return s

def fetch_all_vars(all_vars):
    if not all_vars:
        return None
    assert type(all_vars) is list
    return [fetch_var(var) for var in all_vars]

def fetch_var(var):
    row = variants.loc[lambda df:df['entry_id'] == var]
    assert len(row) == 1
    row = row.loc[0]
    
    row['variant']
    out = 'potato'
    return out
    
def fetch_all_senses(all_senses):
    if not all_senses:
        return None
    elif type(all_senses[0]) is dict():
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
    if var_of_sense and type(var_of_sense[0]) is not dict():
        row['var_of_sense'] = [fetch_var(vos) for vos in var_of_sense]
    out = dict(row)
    return out

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None\
               for row in df[col]]

if __name__ == '__main__':
    main()