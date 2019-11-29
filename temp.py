# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

with open('headword_matches.csv', 'rb') as f:
    lines = f.readlines()
    
with open('headword_matchesNEW.csv', 'w', encoding='utf8') as f:
    f.write('\uFEFF')
    for l in lines:
        f.write(l.decode('utf8').replace('\r',''))