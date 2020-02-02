#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 16:25:02 2020

Removed get_sylls and get_by_sylls from MatchHeadwords.py
Because they weren't really necessary and made the program.
Put them here in a random file in case I ever wanted them
for something.

@author: mark
"""

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
    for i, char in enumerate(s):
        if char in vowels: #possible syllable boundary
            this_syll += char
            out.append(this_syll)
            this_syll='' #reset syllable
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
    return out