#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 20:31:29 2019

@author: marks
"""

import pandas as pd
import json
from PandasExcel import add_bom, remove_bom
from ast import literal_eval

in_file   = 'headword_matches_processed.csv'
default_tags = ('SIL Dict 2011',
                'Weir',
                'Martins',
                'Barbosa')

def main():
    in_df = pd.read_csv(in_file)
    remove_bom(in_df)
    # read col 'variants' as native python types
    in_df.loc[:, 'variants'] = [literal_eval(row) for row in in_df['variants']]
    
    for index, row in in_df.iterrows():
        entry_id = row['entry_id']
        variants = row['variants'] # list of dicts
        
        entry_dict = get_json_dict(entry_id)
        
        merge_dicts(variants, entry_dict)

# adds all entries from dict update to dict source
# asserts that two dicts have no keys in common
def merge_dicts(source, update):
    assert type(source) is dict
    assert type(update) is dict      
    assert not any(k in source for k in update)
    assert not any(k in update for k in source)
    
    for k, v in update:
        pass
    
    source.update(update)

def rep_all(s, chars, tgt):
    for c in chars:
        s = s.replace(c, tgt)
    return s

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

if __name__ == '__main__':
    main()