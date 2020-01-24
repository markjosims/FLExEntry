# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 14:51:21 2020

@author: marks
"""

import pandas as pd
from ast import literal_eval

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None\
               for row in df[col]]
    

bibs = ('sil dict 2011', 'barbosa', 'martins', 'weir', 'cartilhas')

df = pd.read_csv('flexiconNEW.csv', keep_default_na=False)
literal_eval_col(df, 'these_vars')

var_types = set()

for index, row in df.iterrows():
    if 'epps' not in row['bibliography'].lower():
        if not row['these_vars']:
            continue
        
        if 'Predicted phonemic form from source' in row['note']:
            continue
        
        for ref, var_dict in row['these_vars'].items():
            for attr, val in var_dict.items():
                if attr == 'variant-type':
                    val = str(val)
                    var_types.add(val)
                    if any(x in val.lower() for x in bibs):
                        print(row)
                    
print(var_types)