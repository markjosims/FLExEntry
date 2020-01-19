# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:28:10 2020

@author: marks
"""

import pandas as pd
import GenerateLexDir
from datetime import datetime

master = 'flexicon.csv'
sense_file = 'flex_senses.csv'

def main():
    flexicon = pd.read_csv(master, keep_default_na=False)
    senses = pd.read_csv(sense_file, keep_default_na=False)   
    misc_hdwrds = pd.DataFrame( columns=list(flexicon.columns) )
    
    cutoff = datetime(2018, 6, 30)
    read_date = lambda s : datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    
    exclude = ['epps', 'obert', 'liç', 'cartilha']
    
    for index, row in flexicon.iterrows():
        date = row['date'].lower()
        note = row['note'].lower()
        if any(x in note for x in exclude):
            continue
        
        if read_date(date) < cutoff:
            misc_hdwrds.loc[len(misc_hdwrds)] = row
        
    GenerateLexDir.out='misc_entries'
    misc_hdwrds, senses = GenerateLexDir.literal_eval_dfs(misc_hdwrds, senses)
    GenerateLexDir.generate_lex_dir(misc_hdwrds, senses)
    

if __name__ == '__main__':
    main()