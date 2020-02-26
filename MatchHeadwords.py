# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 12:13:52 2019

This program is O(n^2) for a file with 13k lines
Not to mention that each word is divided into syllables,
and that the edit_distance algorithm is run on every
substring compared.
So it's like O( ((s^3)*13,000)^2 ),
where s is the length of a string from a row in in_file.
Don't run it if you expect results in less than an hour.

@author: Mark
"""

import pandas as pd
from LevenshteinSandbox import SmartLevenshtein
from time import time

# decorator
def time_exec(f):
    def g(*args, **kwargs):
        start = time()
        out = f(*args, **kwargs)
        end = time()
        print(str(f), end-start)
        return out
    return g

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

def main():
    df = pd.read_csv(in_file, keep_default_na=False, index_col='entry_id')
    matches = match_dfs(df, df)
    matches.to_csv(out_file, encoding='utf8', index=False)

@time_exec
def match_dfs(df1, df2):
    matches = pd.DataFrame(index=df1.index, columns=['matches'])
    
    for index, row in df1.copy().iterrows():
        broad = row['ipa']
        these_matches = get_matches(broad, df2, index)
        matches.at[index, 'matches'] = these_matches
    
    return matches

# don't call inner funct if first arg is null
# (returns False when cast to bool)
def ignore_null(f):
    def g(s, *args, **kwargs):
        if not s:
            return None
        else:
            return f(s, *args, **kwargs)
    return g

# splits broad transcription into chunks based on syllables
# see get_by_sylls for more info
# looks for matches for each substring
# returns list of all unique matches
@ignore_null
def get_matches(broad, df, this_id):
    matches = {}
    for index, row in df.iterrows():
        ipa = row['ipa']
        headword = row['headword']
        if index == this_id:
            continue
        score = lev.get_distance(broad, ipa, True)
        if score > 0.85:
            matches[index] = (headword, score)

    return matches


if __name__ == '__main__':
    main()

