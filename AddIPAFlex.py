# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 19:53:55 2019

@author: Mark
"""

import pandas as pd
import json
#from ast import literal_eval # uncomment if need to read column data as 
# native python types

in_file = 'flexicon.csv'
with open('CharConversions.json', encoding='utf8') as f:
    char_conversions = json.load(f)

def main():
    df = pd.read_csv(in_file, keep_default_na=False)
    headwords_only = [not x for x in df['variant'] ]
    df = df[headwords_only]
    del headwords_only
    
    ipa = [convert_row(row) for index, row in df.iterrows()]
    headwords = df['headword']
    entry_id = df['entry_id']
    with open("ipa_conv_output.csv", 'w', encoding='utf8') as f:
        f.write('\uFEFFheadword,ipa,entry_id\n')
        for hdwrd, broad, eid in zip(headwords, ipa, entry_id):
            f.write(hdwrd+','+broad+','+eid+'\n')
    

def ignore_null(f):
    def g(s, **kwargs):
        if not s:
            return None
        else:
            return f(s, **kwargs)
    return g

def escape_unicode(s):
    s = s.encode('unicode-escape')
    s = s.decode(encoding='utf8')
    return s

def add_all(s, a):
    assert type(s) is set
    for item in a:
        s.add(item)
        
def convert_row(row):
    if "weir" in row['variant'].lower()\
    or "weir" in row['note'].lower():
        return to_ipa( row['headword'], bib="weir" )
    
    elif "martins" in row['variant'].lower()\
    or "martins" in row['note'].lower():
        return to_ipa( row['headword'], bib="martins" )
    
    elif "barbosa" in row['variant'].lower()\
    or "barbosa" in row['note'].lower():
        return to_ipa( row['headword'], bib="barbosa" )
    
    elif "epps" in row['variant'].lower()\
    or "epps" in row['note'].lower():
        return to_ipa( row['headword'], bib="eppsob" )
    
    elif "sil 2011" in row['variant'.lower()]\
    or "sil 2011" in row['note'].lower():
        return to_ipa( row['headword'], bib="sil" )
    
    else:
        return to_ipa( row['headword'], bib=None)

@ignore_null
def to_ipa(s, bib=None):
    s = s.replace('?', '')
    # for all sources, convert lemma orthography into broad ipa transcription
    out = make_conversions(s)
    out = fix_y(out, bib)
    out = fix_long(out, bib)
    out = fix_lar(out, bib)
    # laryngeal tildes must follow nasal tildes
    out = out.replace('\u0330\u0303', '\u0303\u0330')
    
    return out
    

def make_conversions(s):
    for conversion, conv_dict in char_conversions.items():
        if conversion.startswith('__'):
            continue
        elif '__diac' in conv_dict:
            s = diac_conv(conv_dict, s)
        elif '__singchar' in conv_dict and conv_dict['__singchar']:
            s = singchar_conv(conv_dict, s)
        else:
            assert '__singchar' in conv_dict
            assert not conv_dict['__singchar']
            s = substr_conv(conv_dict, s)
    return s
       
def singchar_conv(d, s):
    for k, v in d.items():
        if k.startswith('__'):
            continue
        for char in k:
            s = s.replace(char, v)
    return s

def substr_conv(d, s):
    for k, v in d.items():
        if k.startswith('__'):
            continue
        s = s.replace(k, v)
    return s

def diac_conv(d, s):
    diac = d['__diac']
    out=s
    for k, v in d.items():
        if k.startswith('__'):
            continue
        for char, target in zip(k, v):
            out = out.replace(char, target+diac)
    return out

def fix_y(s, bib):
    # letter <y> can be /ɨ/ or /j/ depending on source
    if 'y' in s:
        if bib in ('sil', 'eppsob'):
            out = s.replace('y', 'ɨ')
        elif bib == 'weir':
            out = s.replace('y', 'j')
        else:
            assert not bib, bib
            print(f"add bib note for headword {s} indicating source")
            out = s.replace('y', 'ɨ')     
        return out
    else:
        return s
            
def fix_long(s, bib):
    vowels = char_conversions['__vowels']
    nasal_vowels = [v+'\u0303' for v in vowels]
    out = s
    
    for v, nv in zip(vowels, nasal_vowels):
        long_vs = (v+v, nv+v, nv+nv)
        for l_v in long_vs:
            out = out.replace(l_v, l_v[0]+':')
    
    if out != s and bib in ('barbosa', 'martins'):
        # no change should occur for Barbosa or Martins
        assert False, s
        
    return out

def fix_lar(s, bib):
    # lar not marked with tilde beneath
    if bib in ('eppsob', 'sil', 'weir') or not bib:
        if bib == 'weir':
            lar_char = 'x'
        else:
            lar_char = '\u2019'
        
        out = s
        while lar_char in out:
            idx = out.index(lar_char)
            assert len(out) > idx, out
            lar_vowel = out[idx+1]
            assert lar_vowel in char_conversions['__vowels']+['\u0303'], f"headword: {s}, lar_vowel: {lar_vowel}, out: {out}"
            
            out = out.replace(lar_char+lar_vowel, lar_vowel+'\u0330')
        return out
    
    # lar already marked with tilde beneath
    # make sure it's only on vowels
    else:
        prev = ''
        for i, char in enumerate(s):
            if char == '\u0330':
                assert prev in char_conversions['__vowels']+['\u0303'], s
            prev = char
        
        return s

def print_unique(a):
    chars = set()
    for x in a:
        add_all(chars, x)
        
    with open('unique_chars.txt', 'w', encoding='utf8') as f:
        out = str(chars)
        out = escape_unicode(out)
        f.write(out)

if __name__ == '__main__':
    main()