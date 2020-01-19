# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:28:10 2020

@author: marks
"""

import pandas as pd
import GenerateLexDir

master = 'flexicon.csv'
sense_file = 'flex_senses.csv'

def main():
    flexicon = pd.read_csv(master, keep_default_na=False)
    senses = pd.read_csv(sense_file, keep_default_na=False)   
    cartilha_hdwrds = pd.DataFrame( columns=list(flexicon.columns) )  
    exclude = ['epps', 'obert']
    
    for index, row in flexicon.iterrows():
        note = row['note'].lower()
        
        if any(x in note for x in exclude):
            continue
        
        if 'cartilha' in note:
            cartilha_hdwrds.loc[len(cartilha_hdwrds)] = row
        elif 'liç' in note:
            cartilha_hdwrds.loc[len(cartilha_hdwrds)] = row
        
    GenerateLexDir.out='cartilha_entries'
    cartilha_hdwrds, senses = GenerateLexDir.literal_eval_dfs(cartilha_hdwrds, senses)
    GenerateLexDir.generate_lex_dir(cartilha_hdwrds, senses)
    

if __name__ == '__main__':
    main()