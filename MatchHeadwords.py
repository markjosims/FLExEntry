# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 12:13:52 2019

@author: Mark
"""

import pandas as pd
import json
from LevenshteinSandbox import SmartLevenshtein

# configure string comparison object
lev = SmartLevenshtein()
lev.set_weight('ʔh\u0303\u0330:', 0.5)
sim_strs = ('ʔh', 'mw', 'mb', 'pb', 'td', 'dn', 'kg', 'gŋ', 'ŋh', 'ʃc', 'ɲj'\
            'ou', 'oɔ', 'ɨi', 'eɛ', 'əɨ', 'aəʌ')
for ss in sim_strs:
    # chars identified as being "phonologically close" are considered half as
    # far compared to non-similar chars
    lev.set_similar(ss, 1)

in_file = "ipa_conv_output.csv"
out_file = "headword_matches.csv"

in_file = 'flexicon.csv'
with open('CharConversions.json', encoding='UTF-8') as f:
    char_conversions = json.load(f)
    
vowels = char_conversions['__vowels']
cons   = char_conversions['__cons'  ]
clitics = char_conversions['__clitics']
diac = ('\u0330', '\u0303')

def main():
    df = pd.read_csv(in_file, encoding='UTF-8')
    df['matches'] = [None for i in range( len(df) )]
    
    for index, row in df.iterrows():
        lemma = row['headword']
        print(lemma)
        these_matches = get_matches(lemma, df)
        df.loc[index, 'matches'] = these_matches
        
    add_bom(df)
    df.to_csv(out_file)

def ignore_null(f):
    def g(s, *args, **kwargs):
        if not s:
            return None
        else:
            return f(s, *args, **kwargs)
    return g

@ignore_null    
def get_matches(lemma, df):
    by_sylls = get_by_sylls(lemma)
    matches = []
    for substr in by_sylls:
        matches.extend(match_substr(substr, df))

    return list( set(matches) ) # why cast once when you can do it twice?
    
def match_substr(substr, df):
    matches = []
    for index, row in df.iterrows():
        headword = row['headword']
        eid = row['entry_id']
        score = lev.get_distance(substr, headword, True)
        if score > 0.85:
            matches.append( (headword, eid, score) )
    return matches

# arranges list of syllables into list of substrings
# first element is whole word (n syllables)
# next is last n-1 syllables etc.
def get_by_sylls(s):
    sylls = get_syllables(s)
    out = []
    out_str = ''
    for syl in sylls[::-1]:
        out_str = syl+out_str
        out.append(out_str)
    return out[::-1]

# partitions word into syllables
# returns list of strings, each string a single syllable
@ignore_null
def get_syllables(s):
    # force consistent spacing
    s=[x.strip() for x in s.split()]
    # don't consider clitics
    for c in clitics:
        if c in s:
            s.remove(c)
    s=' '.join(s)
    out = []
    this_syll = ''
    prev=''
    for i, char in enumerate(s):
        if char in vowels: #possible syllable boundary
            this_syll += char
            out.append(this_syll)
            this_syll='' #reset syllable
        elif char == ' ': #definite syllable boundary
            assert out, s + ':::' + this_syll
            if prev in cons:
                out[-1]+=this_syll
            this_syll=''
        elif char not in vowels and (char == ' ' or i == len(s)-1):
            #add morpheme-final consonants to previous syllable
            if not out:
                continue
            out[-1]+=this_syll+char
            this_syll=''
        elif char in diac and char != 'ʼ':
            #add diacritics to previous syllable
            if not out:
                continue
            out[-1]+=char
        else:
            this_syll += char #base case
        prev=char
    return out

def add_bom(df):
    cols = df.columns
    first_col = cols[0]
    if '\uFEFF' not in first_col:
        first_col = '\uFEFF' + first_col
        cols = [first_col] + list(cols[1:])
    
    df.columns = cols

if __name__ == '__main__':
    main()

