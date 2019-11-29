# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 17:36:07 2019

@author: Mark
"""

from ReadLiftTags import read_entry, read_sense, step_back
from GenerateLexDir import generate_lex_dir
import pandas as pd

in_file = 'export.lift'
out_file = 'flexicon.csv'
senses_file = 'flex_senses.csv'

def main():
    entries_df = get_entries_df()
    add_bom(entries_df)       
    entries_df.to_csv(out_file, encoding='utf8', index=False)
    remove_bom(entries_df)

    senses_df = get_senses_df()
    add_bom(senses_df)
    senses_df.to_csv(senses_file, encoding='utf8', index=False)
    remove_bom(senses_df)
    
    generate_lex_dir(entries_df, senses_df)
  
def get_entries_df():
    entries_df = pd.DataFrame(columns = ['headword', 'entry_id', 'morph_type',
                                 'pronunciation', 'variant', 'note', 'sense'])
    with open(in_file, 'rb') as f:
        line_bytes = f.readline()
        while line_bytes:
            line_str = line_bytes.decode('utf8').strip()
            
            if line_str == '</lift>':
                break
            
            assert line_str.startswith('<entry'), line_str
            step_back(f, line_bytes)
            this_entry = read_entry(f)
            entries_df.loc[len(entries_df)] = this_entry
            
            line_bytes = f.readline()  
            
    return entries_df

def get_senses_df():
    senses_df = pd.DataFrame(columns = ['sense_id', 'pos', 'gloss', 'def',\
                                       'reverse', 'note'])
    with open(in_file, 'rb') as f:
        line_bytes = f.readline()
        while line_bytes:
            line_str = line_bytes.decode('utf8').strip()
            
            if line_str == '</lift>':
                break
            
            if line_str.startswith('<sense'):
                step_back(f, line_bytes)
                this_sense = read_sense(f)
                senses_df.loc[len(senses_df)] = this_sense
                
            line_bytes = f.readline()
    
    return senses_df
    
def add_bom(df):
    cols = df.columns
    first_col = cols[0]
    if '\uFEFF' not in first_col:
        first_col = '\uFEFF' + first_col
        cols = [first_col] + list(cols[1:])
    
    df.columns = cols
    
def remove_bom(df):
    cols = df.columns
    first_col = cols[0]
    if '\uFEFF' in first_col:
        first_col = first_col.replace('\uFEFF', '')
        cols = [first_col] + list(cols[1:])
    
    df.columns = cols

def return_dfs():
    return get_entries_df(), get_senses_df()
          
if __name__ == '__main__':
    main()