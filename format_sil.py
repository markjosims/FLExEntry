# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 14:50:46 2019

@author: Mark
"""


pos_tags = ('adj.', 'adv.', 'conj.', 'intj.', 'n.', 'n op.', 'onom.',\
            'n_p.', 'posp.', 'prep.', 'pro.', 's.', 's op.',\
            'v.', 'v_s.', 'v_p.', 'v p', 'negativo.', 'imperativo.', 'v imp.',\
            'v_ pl.', 'adv op.', 'n esp.', 'par.', 'suf.', 'v_imp.', 'v_pl.')

in_file = 'sil_nadeb_dict.txt.'
out_file = 'sil_nadeb_dict.csv'

global pos
pos = set()

def main():
    with open(in_file, 'r', encoding='utf8') as f:
        d=find_def_and_variants(f)
    
    with open(out_file, 'w', encoding='utf8') as f:
        for key, val in d.items():
            f.write(key+','+','.join(val))
            f.write('\n')


    
def find_def_and_variants(f):
    d = dict()
    last_key = None
    for line in f:
        line = line.replace('\n', '')
        line = line.replace(',', ';')
        if (not line.startswith(' '*7)) and any(tag in line for tag in pos_tags):
            idcs = []
            for tag in pos_tags:
                if tag in line:
                    idcs.append(line.index(tag))
            idx = min(idcs)
            last_key = line[:idx].strip()
            d[last_key] = [line[idx:]]
        elif line.startswith(' '*8):
            d[last_key][-1] += line
        else:
            assert last_key
            d[last_key][0] += line
    d_c = d.copy()
    for key, val in d_c.items():
        new_vals = val
        temp = val[0]
        for sub in temp.split(sep='.'):
            if ':' in sub:
                temp = temp.replace(sub+'.', '')
                new_vals.append(sub)
        new_vals = [x.strip() for x in new_vals]
        d[key] = new_vals
    return d

def get_lemma_pos_def(s):
    idcs = []
    tags = []
    for tag in pos_tags:
        if tag in s:
            idcs.append(s.index(tag))
            tags.append(tag)
    if not idcs:
        return False, False
    this_idx = min(idcs)
    idx_of_idx = idcs.index(this_idx)
    this_tag = tags[idx_of_idx]
    return this_idx, this_tag

main()