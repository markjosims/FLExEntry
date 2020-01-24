#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 07:13:32 2020

@author: mark
"""

import json
import pandas as pd
from ast import literal_eval
from datetime import datetime
from GenerateLexDir import main as gld
#from PandasExcel import remove_bom, add_bom

master = 'flexicon.csv'
martins_file = 'MartinsDatabase.csv'
barbosa_file = 'BarbosaDatabase.csv'
 
def main():
    martins_df = pd.read_csv(martins_file)
    barbosa_df = pd.read_csv(barbosa_file)
    flexicon = pd.read_csv(master, index_col = 'entry_id', keep_default_na=False)
    literal_eval_col(flexicon, 'note')
    #literal_eval_col(flexicon, 'variant_of')
    
    martins = list( martins_df['martins'] )
    barbosa = list( barbosa_df['barbosa'] )
    unexpected = list( martins_df['barbosa'] )
    
    cutoff = datetime(2018, 6, 30)
    read_date = lambda s : datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    
    bib_col = []
    
    for index, row in flexicon.iterrows():
        bib=''
        variant = row['variant_of'].lower() if row['variant_of'] else ''
        assert type(variant) is str, variant
        note = row['note'] if row['note'] else {}
        note_str = str(note).lower()
        date = read_date(row['date'])
        hdwrd = row['headword'].strip()
        
        if 'bibliography' in note.keys():
            bib = note.pop('bibliography')
            if bib == 'SIL 2011':
                bib = 'SIL Dict 2011'
            bib = bib[0] if len(bib)==1 else bib
            
        elif 'martins' in variant or 'martins' in note_str:
            bib='Martins'
        elif 'barbosa' in variant or 'barbosa' in note_str:
            bib='Barbosa'
        elif 'weir' in variant or 'weir' in note_str:
            bib='Weir'
        elif date > cutoff:
            bib='Fieldnotes Epps/Obert; 2018'
            
        elif hdwrd in martins:
            bib='Martins'
        elif hdwrd in barbosa:
            bib='Barbosa'
        else:
            assert hdwrd not in unexpected, row
        
        bib_col.append(bib)
    
    print(bib_col.count(''))
    flexicon['bibliography'] = bib_col
    flexicon.to_csv('flexicon.csv')
    gld()
        
        

def get_json_dict(eid):
    filehead = eid
    filehead = rep_all(filehead, '/\\ ', '_')
    filehead = rep_all(filehead, '()[]? ', '')
    filehead = filehead.replace('_=', '=')
    filename = 'entries\\' + filehead + '.json'
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