# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 11:02:55 2019

@author: Mark
"""

import pandas as pd
from ast import literal_eval
from collections import defaultdict
from PandasExcel import add_bom

in_file = 'headword_matches.csv'
out_file = 'headword_matchesNEW.csv'

def main():
    df = pd.read_csv(in_file, encoding='utf8')
    df.loc[:, 'matches'] = [literal_eval(row) for row in df['matches']]
    
    def avg_len(l):
        len_sum = sum( len(x) for x in l )
        return len_sum / len(l)
    
    df.loc[:, 'matches'] = [remove_repeat_ids(row) for row in df['matches']]
    
    add_bom(df)
    df.to_csv(out_file, index=False)
    

# matches is a list of tuples
# each tuple of the shape (headword, id, score)
# returns list of same shape, but with tuples of
# the same id removed
def remove_repeat_ids(matches):
    ids = defaultdict( lambda : ('', 0) )
    for m in matches:
        headword = m[0]
        m_id     = m[1]
        score    = m[2]
        if ids[m_id][1] < score:
            ids[m_id] = (headword, score)
    
    return [(v[0], k, v[1]) for k, v in ids.items()]

if __name__ == '__main__':
    main()