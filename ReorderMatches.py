# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 11:34:57 2019

Using user input, identifies headwords that match other headwords
as variants of a single headword.

Outputs dataframe containing solely entry ids and variant types indicating
relations.

@author: Mark
"""

import pandas as pd
import json
from os import path
from shutil import copyfile
from PandasExcel import add_bom, remove_bom
from ast import literal_eval

in_file     = 'headword_matches_unprocessed.csv'
out_file    = 'headword_matches_processed.csv'
unused_file = 'unused_headwords.json'

def main():
    write_backup(in_file)
    write_backup(out_file)
    
    global in_df, out_df, unused_entries
    in_df =  pd.read_csv(in_file)
    out_df = pd.read_csv(out_file)
    with open(unused_file, 'r') as f:
        unused_entries = json.load(f)
   
    # read col 'matches' as native python types
    in_df.loc[:, 'matches'] = [literal_eval(row) for row in in_df['matches']]
    
    remove_bom(in_df)
    remove_bom(out_df)
    
    order_matches()
    
    write_result(in_df,     in_file)
    write_result(out_df,    out_file)
    with open(unused_file, 'w') as f:
        json.dump(unused_entries, f)
    
# iterates thru matches data
# asks user to decide how to structure entries
# deletes all entries that have been processed from in_df
def order_matches():
    copy = in_df.copy()
    for index, row in copy.iterrows():
        if row['entry_id'] not in list( in_df['entry_id'] ):
            continue
        if not row['matches']:
            continue
        ordered, ids = get_order(row)
        if not ordered:
            # 'esc' was passed as input
            # print dfs as they are
            return
        edit_dfs(ordered, ids)
        
# prints entry id and headword form of all entries referenced in row
# asks user to specify which form is the main entry, which are the variants
# and what variant types they are
def get_order(row):
    ids = [row['entry_id']] + [m[1] for m in row['matches']]
    headwords = [row['headword']] + [m[0] for m in row['matches']]
    json_dicts = [get_json_dict(i) for i in ids]
    glosses = [get_gloss(j) for j in json_dicts]
    bibs    = [get_bib(j)   for j in json_dicts]
    dates   = [j['date']  for j in json_dicts]
    for i, (eid, hdwrd, gls, bib, date) \
    in enumerate( zip(ids, headwords, glosses, bibs, dates) ):
        print(f"{i}: {hdwrd}- {gls}- {bib}- {date}")
    print("How would you like to organize these entries?")
    print("Please input a string of integers indicating your choice "+\
          "for each entry.")
    print("2 to set as headword, 1 to set as variant, 0 to set as unrelated.")
    print("Type 'esc' to leave the program and save progress.")
    print( ''.join( str(i) for i, _ in enumerate(ids) ) , end='' )
    result = input()
    result = validate_result(result, len(ids))
    if result == -1:
        return None, None
    return result, ids

# given result, a string describing hierarchy of entry ids in list ids
# edit in_df and out_df to this data heirarchy
def edit_dfs(result, ids):
    global in_df, out_df, unused_entries
    # base case, no headword or variants
    # ignore all entries, add main to unused_entries
    if '2' not in result:
        unused_entries.append(ids[0])
    # if a headword is present, but the main id is not it nor a variant of it
    print([id_in_df(i) for i in ids])
    
    
def id_in_df(eid):
    match_ids = [m[1] for match in in_df['matches'] for m in match]
    result = eid in match_ids or eid in list(in_df['entry_id'])
    if not result:
        print(in_df['entry_id'])
        print(f'id not found {eid}')
    return result
 
# checks if string result fits acceptance conditions
# prompts user for correction until conditions are met
# returns string
def validate_result(result, size):
    if result == 'esc':
        return -1
    while True:
        try:
            assert len(result) == size
            for char in result:
                assert char in ('0', '1', '2')
            assert result.count('2') <= 1
            # can't have variants if no headword is identified
            if '2' not in result:
                assert '1' not in result
            int(result)
            return result
        except (ValueError, AssertionError):
            print("Please type only ints in the range 0-2 in a string of len",\
                  size)
            result = input()
    
def get_json_dict(eid):
    filehead = eid
    filehead = rep_all(filehead, '/ ', '_')
    filehead = rep_all(filehead, '()[]? ', '')
    filename = 'entries/' + filehead + '.json'
    with open(filename, 'r', encoding='utf8') as f:
        lemma = json.load(f)
    return lemma

def get_gloss(lemma):
    for sense in lemma['sense']:
        # return gloss if gloss has nonzero value
        if sense['gloss']:
            # gloss is stored as a dictionary w/ language as keys
            # which language is returned is unimportant, so
            # return a random value
            return sense['gloss'].popitem()[1]
        # return definition if def has nonzero value
        elif sense['def']:
            return sense['def'].popitem()[1]  
    # tough luck, no data on lexeme meaning
    else:
        return None

def get_bib(lemma):
    if lemma['note']:
        for note in lemma['note']:
            if note[1] == 'bibliography':
                return note[0]
    return None
    
def rep_all(s, chars, tgt):
    for c in chars:
        s = s.replace(c, tgt)
    return s

# checks that backup file does not currently exist
# write backup as copy of main
def write_backup(f):
    f_backup = f.split(sep='.')
    f_backup[0] += 'BACKUP'
    f_backup = '.'.join(f_backup)
    
    #assert not path.exists(f_backup), f"Make sure {f} is satisfactory "\
    #+f"and then delete {f_backup}"
    
    copyfile(f, f_backup)
    
# check that files are not open
# wait for user input if so, then write df
def write_result(df, file):
    while True:
        try:
            add_bom(df)
            df.to_csv(file, encoding='utf8', index=False)
            break
        except:
            input(f"{file} is currently in use by another program. Please "\
                  +"close it so that the results may be saved.")
        
if __name__ == '__main__':
    main()