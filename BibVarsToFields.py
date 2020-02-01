# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:59:39 2020

@author: marks
"""

import pandas as pd
from ast import literal_eval

bibs = ('sil dict 2011', 'barbosa', 'martins', 'weir', 'cartilhas')
in_file = 'flexiconNEW.csv'
out_file = 'flexiconHDWRDS.csv'

def main():
    flexicon = pd.read_csv(in_file, index_col='entry_id', keep_default_na=False)
    print(len(flexicon))
    flexicon['other_sources'] = lambda : None
    literal_eval_col(flexicon, 'these_vars')
    flexicopy = flexicon.copy()
    
    for index, row in flexicopy.iterrows():
        these_vars = row['these_vars'] if row['these_vars'] else {}
        
        these_bib_vars = {}
        # drop all entries that correspond to a bibliographic variant
        for v_id, v_dict in these_vars.items():
            if 'variant-type' not in v_dict:
                continue
            bib = get_bib(v_dict['variant-type'])
            if not bib:
                continue
            
            these_bib_vars[bib] = flexicon.at[v_id, 'headword']
            flexicon.drop(v_id, inplace=True)
        if not these_bib_vars:
            continue
        assert index in flexicon.index, index
        flexicon.at[index, 'other_sources'] = str(these_bib_vars)
    
    print(len(flexicon))
    
    flexicon.to_csv(out_file)

def literal_eval_col(df, col):
    df.at[:, col] = [literal_eval(row) if row else None\
               for row in df[col]]
    
def get_bib(bib, epps_ob=False):
    bib = str(bib).lower()
    if "weir" in bib:
        return "Weir"
    
    elif "martins" in bib:
        return "Martins"
    
    elif "barbosa" in bib:
        return "Barbosa"
    
    elif "sil" in bib:
        return "Sil Dict 2011"
    
    elif "cartilha" in bib or 'liç' in bib:
        return "Cartilhas"
    
    elif not bib:
        return 'undef'
    
    elif epps_ob and 'epps' in bib:
        return 'Fieldnotes Epps/Obert; 2018'
    
    else:
        return None

if __name__ == '__main__':
    main()