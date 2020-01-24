# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 22:06:42 2020

@author: marks
"""

import pandas as pd
from GenerateLexDir import main as to_json
from ast import literal_eval

in_file = 'flexicon.csv'
out_file = 'cartilha_data.csv'

def main():
    global flexicon
    flexicon = pd.read_csv(in_file, keep_default_na=False, index_col='entry_id')
    literal_eval_col(flexicon, 'these_vars')
    literal_eval_col(flexicon, 'variant_of')
    print(len(flexicon))
    cartilhas = pd.DataFrame(columns=flexicon.columns)
    for index, row in flexicon.copy().iterrows():
        row_str = str(row).lower()
        if 'cartilha' in row_str:
            remove_from_df(index)
            flexicon = flexicon.drop(index)
            cartilhas.loc[ len(cartilhas) ] = row
    print(len(flexicon))
    print(len(cartilhas))
    
    flexicon.to_csv(in_file, index=False)
    cartilhas.to_csv(out_file, index=False)
    to_json()
    
def remove_from_df(eid):
    assert type(eid) is str, eid
    for index, row in flexicon.iterrows():
        these_vars = row['these_vars']
        var_of = row['variant_of']
        
        assert not var_of or eid not in var_of, flexicon.loc[eid]
        
        if not these_vars:
            continue
        
        if eid in these_vars:
            these_vars.pop(eid)
            flexicon.at[index, 'these_vars'] = these_vars

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None for row in df[col]]    

if __name__ == '__main__':
    main()