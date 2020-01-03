#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 07:13:32 2020

@author: mark
"""

import json
import pandas as pd
from ast import literal_eval
#from PandasExcel import remove_bom, add_bom

in_file = 'headword_matches_processed.csv'
master = 'flexicon.csv'
martins_file = 'MartinsDatabase.csv'
barbosa_file = 'BarbosaDatabase.csv'
 
def main():
    martins_df = pd.read_csv(martins_file)
    barbosa_df = pd.read_csv(barbosa_file)
    flexicon = pd.read_csv(master, index_col = 'entry_id')
    in_df = pd.read_csv(in_file)
    
    literal_eval_col(in_df, 'variants')
    flexicon = flexicon['headword']
    
    martins = list( martins_df['martins'] )
    barbosa = list( barbosa_df['barbosa'] ) + list( martins_df['barbosa'] )
    
    for index, row in in_df.iterrows():
        new_row = {}
        for var_id, var_type in row['variants'].items():
            if var_type != 'undef':
                new_row[var_id] = var_type
            else:
                headword = flexicon[var_id]
                if headword in martins:
                    new_row[var_id] = 'Martins'
                elif headword in barbosa:
                    new_row[var_id] = 'Barbosa'
                else:
                    new_row[var_id] = 'undef'
        
        if new_row == dict(row):
            continue
        print(new_row)
        in_df.at[index, 'variants'] = new_row
        
    in_df.to_csv('headword_matches_processedNEW.csv')

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