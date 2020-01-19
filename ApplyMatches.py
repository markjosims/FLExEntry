#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 20:31:29 2019

@author: marks
"""

import pandas as pd
import json
from ast import literal_eval
from time import time
from GenerateLexDir import main as to_json

# decorator
def time_exec(f):
    def g(*args, **kwargs):
        start = time()
        f(*args, **kwargs)
        end = time()
        print(str(f), end-start)
    return g


in_file = 'headword_matches_processed.csv'
out_file = 'headword_matches_remaining.csv'
master  = 'flexicon.csv'
default_tags = ('SIL Dict 2011',
                'Weir',
                'Martins',
                'Barbosa',
                'Cartilhas')

@time_exec
def main():
    in_df = pd.read_csv(in_file, index_col='entry_id', keep_default_na=False)
    flexicon = pd.read_csv(master, index_col='entry_id', keep_default_na=False)
    
    # read col 'these_vars' as native python types
    literal_eval_col(in_df, 'variants')
    literal_eval_col(flexicon, 'these_vars')
    literal_eval_col(flexicon, 'variant_of')
    
    print(len(flexicon))
    for entry_id, row in in_df.iterrows():
        assert entry_id in in_df.index
        variants = row['variants'] # list of dicts
        
        entry_row = flexicon.loc[entry_id]
        these_vars = entry_row['these_vars']
        these_vars = {} if not these_vars else these_vars
        transfer_variants(these_vars, variants, flexicon)
        
        if not these_vars:
            continue
        
        # update in_df so transferred tags are removed
        in_df.at[entry_id, 'variants'] = variants
        
        # add new variants to flexicon
        flexicon.at[entry_id, 'these_vars'] = these_vars
        
        # update variant_of for each of these_vars
        for var_id, var_type in these_vars.items():
            variant_of = flexicon.at[var_id, 'variant_of']
            variant_of = {} if not variant_of else variant_of
            variant_of[entry_id] = var_type
            flexicon.at[var_id, 'variant_of'] = variant_of
    
    # ignore rows w/ empty data
    print(len(flexicon))
    has_data = [bool(x) for x in in_df['variants']]
    print(len(in_df))
    in_df = in_df[has_data]
    print(len(in_df))
    
    in_df.to_csv(out_file)
    flexicon.to_csv(master) 
    to_json()


# adds all entries from dict update to dict source
# asserts that two dicts have no keys in common
def transfer_variants(source, update, flexicon):
    assert type(source) is dict, source
    assert type(update) is dict, update
    assert not any(k in source for k in update)
    assert not any(k in update for k in source)
    
    for k, v in update.copy().items():
        if v in default_tags:
            source[k] = update.pop(k)
        elif 'DELETE' in v.upper():
            update.pop(k)
            flexicon.drop(k, inplace=True)

def get_json_dict(eid):
    filehead = eid
    filehead = rep_all(filehead, '/ ', '_')
    filehead = rep_all(filehead, '()[]? ', '')
    filehead = filehead.replace('_=', '=')
    filename = 'entries/' + filehead + '.json'
    while True:
        try:
            with open(filename, 'r', encoding='utf8') as f:
                lemma = json.load(f)
            return lemma
        except FileNotFoundError:
            print(f'Could not find {filename}. Please enter the correctly'+\
                  ' typed json file below:')
            filename = input()
            
def rep_all(s, chars, tgt):
    for c in chars:
        s = s.replace(c, tgt)
    return s

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None for row in df[col]]

if __name__ == '__main__':
    main()