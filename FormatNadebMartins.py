# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 20:20:38 2019

@author: Mark
"""

import pandas as pd
from collections import defaultdict
import numpy as np
from LevenshteinSandbox import SmartLevenshtein
lev = SmartLevenshtein()
lev.set_weight('ʔh\u0303\u0330:', 0.5)
sim_strs = ('ʔh', 'mw', 'mb', 'pb', 'td', 'dn', 'kg', 'gŋ', 'ŋh', 'ʃc', 'ɲj'\
            'ou', 'oɔ', 'ɨi', 'eɛ', 'əɨ', 'aəʌ')

for ss in sim_strs:
    lev.set_similar(ss, 1)

vowels = ('i', 'ɯ', 'u',\
          'e', 'ɤ', 'o',\
          'ɛ', 'ʌ', 'ɔ',\
          'a', 'õ')
vowel_phon = ('i', 'ɨ', 'u',\
              'e', 'ə', 'o',\
              'ɛ', 'ʌ', 'ɔ',\
              'a', 'o\u0303')

cons = ('m', 'n', 'ɲ', 'ŋ',\
        'p', 't', 'c', 'k', 'ʔ',\
        'b', 'd', 'ɟ', 'g',\
        's', 'ʃ', 'h',\
        'w', 'r', 'l', 'ɾ', 'j')
con_phon = ('m', 'n', 'ɲ', 'ŋ',\
            'p', 't', 'c', 'k', 'ʔ',\
            'b', 'd', 'c', 'g',\
            'ʃ', 'ʃ', 'h',\
            'w', 'r', 'r', 'r', 'j')
conts = ('bm', 'dn', 'ɟɲ', 'gŋ', 'kŋ', 'kʼ')
simps = ('m', 'n', 'ɲ', 'ŋ', 'ŋ', 'g')

diac = ('\u0330', '\u0303', ':', 'ʼ', "'")
ignore = ('ɵ', '\u031D', '-', '\u031A', 'ə', 'ʝ', ';', "'", '\u0334')

# data files
in_file = 'epps_cognate_database.csv'
flex_file = 'nadeb_lexicon.csv'
out_file = 'nadeb_possible_matches.csv'

# all row entries that indicate no data
null = (np.nan, '--', 'NF', 'NC')

def main():
    df = pd.read_csv(in_file)
    eppsob_df = pd.read_csv(flex_file)
    
    # get rid of data that ain't data
    for n in null:
        df = df.replace(n, '', regex=True)
        eppsob_df = eppsob_df.replace(n, '', regex=True)
    rio_negro = df['Nadëb Rn m05']
    rocado = df['Nadëb Rç m05']
    lexemes = tuple(rn +' '+ rc for rn, rc in zip(rio_negro, rocado))
    phonemic = tuple(format_martins(l) for l in lexemes)
    glosses = tuple(df['gloss_pt'])
    martins = tuple((ph, l, g) for ph, l, g in zip(phonemic, lexemes, glosses) if ph)
    
    orth = eppsob_df['Orth']
    phon = eppsob_df['Phon']
    gloss = eppsob_df['Gloss']
    date = eppsob_df['Date']
    eppsob = tuple([o,p,g,d] for o, p, g, d in zip(orth, phon, gloss, date))
    
    print(martins[:3])
    print(eppsob[:3])
    
    matches = find_matches(martins, eppsob)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('\uFEFFm05 form,m05 gloss,eppsob form,eppsob phonem,eppsob gloss,date,score\n')
        for k, v in matches.items():
            for entry in v:
                f.write(k+','+entry+'\n')

def ignore_null(f):
    def g(s):
        if not s:
            return None
        else:
            return f(s)
    return g

# iterates thru new_entries
# finds high-scoring matches in old_entries
# returns dictionary where old_entries are keys
# and sets of matches from new_entries are values
def find_matches(old_entries, new_entries):
    matches = defaultdict(set)
    
    for new in new_entries:
        #print('new', new)
        if not new:
            continue
        new_lx = new[1]
        new_lx = new_lx.replace('tʃʼ', 'c')
        new_lx = new_lx.replace('kʼ', 'g')
        for old in old_entries:
            old_lx = old[0]
            scores = []
            for sub in new_lx.split():
                sylls = get_syllables(sub)
                score_str = ''
                for sl in sylls[::-1]:
                    score_str = sl + score_str
                    this_score=[]
                    for sub in old_lx:
                        this_score.append(string_diff(sub, score_str))
                    scores.append(max(this_score))
            if scores and max(scores) >= 0.70:
                matches[','.join(old[1:])].add(','.join(new+[str(max(scores))]))
                
    # turns the dict values from sets into tuples
    matches = {k:tuple(v) for k, v in matches.items()} 
    return matches
        
@ignore_null
def format_martins(s):
    phon_s = s
    # ignore that which is to be ignored
    for i in ignore:
        if i in phon_s:
            phon_s = phon_s.replace(i, '')
    # replace martins vowel letters for phonemic vowel letters
    for v, v_p in zip(vowels, vowel_phon):
        if v in phon_s:
            phon_s = phon_s.replace(v, v_p)
    # replace martins consonant letters for phonemic consonant letters
    for c, c_p in zip(cons, con_phon):
        if c in phon_s:
            phon_s = phon_s.replace(c, c_p)
    # remove combining tilde from consonants
    temp=''
    for i, char in enumerate(phon_s):
        prev = phon_s[i-1] if i != 0 else ''
        if char == '\u0330' and prev in con_phon:
            continue
        else:
            temp+=char
    phon_s=temp
    # remove space adjacent to apostrophe
    while ' ʼ' in phon_s or 'ʼ ' in phon_s or 'ʼʼ' in phon_s:
        phon_s = phon_s.replace(' ʼ', 'ʼ')
        phon_s = phon_s.replace('ʼ ', 'ʼ')
        phon_s = phon_s.replace('ʼʼ', 'ʼ')
    # replace contour segments w/ underlying phoneme
    for ct, sim in zip(conts, simps):
        phon_s = phon_s.replace(ct, sim)
    phon_s = phon_s.replace('ʔ', '')
    phon_s = phon_s.replace('\u0303\u0330', '\u0330\u0303') # lar then nasal
    phon_s = phon_s.strip()
    
    return phon_s

# partitions word into syllables
# returns list of strings, each string a single syllable
def get_syllables(s):
    s=' '.join(x.strip() for x in s.split())
    out = []
    this_syll = ''
    prev=''
    for i, char in enumerate(s):
        if char in vowel_phon: #possible syllable boundary
            this_syll += char
            out.append(this_syll)
            this_syll='' #reset syllable
        elif char == "'" or char == ' ': #definite syllable boundary
            if prev in con_phon:
                out[-1]+=this_syll
            this_syll=''
        elif char not in vowel_phon and (char == ' ' or i == len(s)-1):
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
           
# wrapper function for string comparison 
def string_diff(s1, s2):
    return lev.get_distance(s1, s2, True)


if __name__ == '__main__':
    main()