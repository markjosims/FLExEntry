# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 12:39:59 2019

@author: Mark
"""

import pandas as pd

df = pd.read_csv('flexicon.csv')

initial_morphemes = [hdwrd.split()[0] for hdwrd in df['headword']]
final_morphemes = [hdwrd.split()[-1] for hdwrd in df['headword']]
morphemes = initial_morphemes + final_morphemes
clitics = [m for m in morphemes if initial_morphemes.count(m) > 3\
           or final_morphemes.count(m) > 4]
clitics = set(clitics)
clitics = list(clitics)

with open('clitics.txt', 'w', encoding='utf8') as f:
    f.write( str(clitics) )