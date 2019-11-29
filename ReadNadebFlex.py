# -*- coding: utf-8 -*-
"""
Created on Thu May 23 18:48:47 2019

Reads 'full lexicon', text file w/ .db extension, as exported by FLEx
Writes csv with select data for each lexeme
Configured for Nadëb language

@author: Mark_S
"""
mismatch=0
in_file = 'nadeb_flex_full_lex.db'
out_file = 'nadeb_lexicon.csv'

# tuples and pointers for orthography
# used for conversion btw practical and working
# vowel qualities in practical and phonemic orth
orth_v = ('i', 'y', 'u',\
          'e', 'ë', 'o',\
          'é', 'ä', 'ó',\
          'a')
phon_v = ('i', 'ɨ', 'u',\
          'e', 'ə', 'o',\
          'ɛ', 'ɐ', 'ɔ',\
          'a')

# consonants in practical and phonemic orth
orth_c = ('m', 'n', 'nh', 'ng',\
          'p', 't', 'k',\
          'b', 'd', 'ts', 'g',\
          's', 'h',\
          'w', 'r', 'j')
phon_c = ('m', 'n', 'ɲ', 'ŋ',\
          'p', 't', 'k',\
          'b', 'd', 'tʃ', 'g',\
          'ʃ', 'h',\
          'w', 'ɾ', 'j')

# nasal equivalents of all vowels in practical and phonemic orth
# mid-high series does not exist nasalized: 'N\\A' strings serve as
# error flags
orth_nasal = ('ĩ', 'ỹ', 'ũ',\
              'N\\A', 'N\\A', 'N\\A',\
              'ẽ', 'ä\u0303', 'õ',\
              'ã')
phon_nasal = ('i\u0303', 'ɨ\u0303', 'u\u0303',\
              'N\\A', 'N\\A', 'N\\A',\
              'ɛ\u0303', 'ɐ\u0303', 'ɔ\u0303',\
              'a\u0303')

# vowels with combining diacritics and their equivalent w/ fused diacritics
combin = ('i\u0303', 'y\u0303', 'u\u0303',\
          'e\u0303', 'e\u0308', 'o\u0303',\
          'e\u0301', 'a\u0308', 'o\u0301',\
          'a\u0303')
fused =  ('ĩ', 'ɨ\u0303', 'ũ',\
          'ɛ\u0303', 'ə', 'ɔ\u0303',\
          'ɛ', 'ɐ', 'ɔ',\
          'ã')

# mid high vowels with nasal markers and their mid low equivalents
mid = {'ɛ\u0303': ('ẽ', 'e\u0303'), 'ɔ\u0303': ('õ', 'o\u0303')}

# allophonic manifestations of ejective consonants
eject = {'kʼ':('ʔkʼ', 'ʔk', 'kʼ', 'g'),\
         'tʃʼ':('ʔtʃʼ', 'ʔtʃ', 'tʃʼ', 'ɟ')}


# combined lists for iteration ease
all_orth = orth_v + orth_c + orth_nasal + combin
all_phon = phon_v + phon_c + phon_nasal + fused
all_vowels = phon_v + phon_nasal



# all flags used in the lexicon to mark the gloss/definition of an entry
def_flags = ('\\g_Eng', '\\g_Por', '\\d_Eng', '\\d_Por', '\\re_Eng', '\\re_Por',
             '\\su_Por')
def_langs = ('(eng)', '(por)', '(eng)', '(por)', '(eng)', '(por)',
             '(por)')
phon_flags = ('\\ph_Por', '\\ph_Nad')
lex_flags = ('\\lx', '\\lx_Nad')

# month abbreviations and their number equivalents
month_abrevs = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',\
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
month_index = tuple(str(i) for i in range(1,13))

# misc chars in phonetic orth not copied into phonemic
ignore = "ˈ\u02FA\u031A[]()?."

# chars written as spaces in phonemic
spaces = "-/="

# pointers for nasal contours and their underlying/simple realizations
conts = ('bm', 'dn', 'ɟɲ', 'gŋ')
simps = ('m', 'n', 'ɲ', 'ŋ')

# chars in phonetic transcription w/ simple replacements in phonemic
phonet = 'ǝʌː'
phonem = 'əɐ:'


def main():
    with open(in_file, 'r', encoding='utf8') as f:
        lexemes = []
        line = f.readline()
        while line: # until EOF
            if line.split() and line.split()[0] == '\\lx': # new lexeme detected
                lex_fields = {} # dictionary to store all fields for entry
                while line and line != '\n':
                    # read all fields for current lexeme
                    lex_fields[line.split()[0]] = ' '.join(line.split()[1:])
                    line = f.readline()
                    
                orth = lex_fields['\\lx']
                if not orth:
                    continue
                if any(char in orth for char in 'ʉxɨ'): # weir data
                    continue
                orth = orth.replace('=', '')
                definition = get_definition(lex_fields)
                if not definition:
                    continue
                phonetic = get_phonemic(lex_fields)
                if not phonetic:
                    continue
                
                for ph in phonetic:
                    entry = (orth, ph, definition)
                    entry = (x.replace(',', ';') for x in entry)
                    entry = (x.replace('\\;', ',') for x in entry)
                    lexemes.append(entry)
                
            line = f.readline()
        
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('\uFEFFOrth,Phon,Gloss,Date\n')
        for entry in lexemes:
            f.write(','.join(entry)+'\n')
    print(mismatch)
    
def ignore_null(f):
    def g(s):
        if not s:
            return None
        else:
            return f(s)
    return g

    
# feeds dictionary containing all lexical flags of a FLEx entry
# finds field containing definition, whichever applicable is found first
# returns as string
def get_definition(fields):
    date = fields['\dt'].lower()
    for ma, mi in zip(month_abrevs, month_index):
        date=date.replace(ma, mi)
    for flag, lang in  zip(def_flags, def_langs):
        # prioritize Eng gloss, then Eng def, then Port def
        if flag in fields.keys():
            if fields[flag] == '?':
                continue # don't include blank definitions
            return fields[flag] +' '+ lang + '\\;' + date
            # substring indicating language of datum
    
# feeds dictionary containing all lexical flags of a FLEx entry
# finds field containing phonetic orthography
# if not found, generates phonetic orth from practical
# returns str
# NOTE: fix to return both auto-gen phonemic and FLEx phonetic data
# if two are different
# also account for entries w/ multiple lexemes listed
# note which punctuation is used in such instances
def get_phonemic(fields):
    # initialize return var to list with phonetic data auto-gen'd from
    # lexeme field
    from_lex = orth_to_work(fields['\\lx'])
    out_list=[from_lex]
    global mismatch
    # try to find field w/ phonetic data from FLEx
    for flag in phon_flags:
        if flag in fields.keys():
            # if doesnt match auto-gen'd phonemic string, add as separate entry
            from_phon = phonet_to_phonem(fields[flag])
            if from_phon != from_lex:
                #print(f"from_phon: {from_phon}, from_lex: {from_lex}, lex: {lex}")
                mismatch+=1
                out_list.append(from_phon)
    return out_list
            
@ignore_null
# converts a string in phonetic orthography to phonemic
def phonet_to_phonem(phonet_str):
    out=ptp_replace(phonet_str)
    out=ptp_fix_nasals(out)
    out=ptp_fix_ejects(out)
    out=ptp_fix_lar(out)
    return out

### phonet_to_phonem helper methods ###
    
# perform simple replacements, exclude irrelevant chars
def ptp_replace(s):
    out=''
    for i, char in enumerate(s):
        folw = s[i+1] if len(s)>i+1 else ''
        prev = s[i-1] if i>0 else ''
        if char == 'ʔ' and (not folw or folw == ' '):
            # ignore word-final glottal stop
            pass
        elif char in 'əᵊ' and (not folw or folw == ' ') and prev == 'ɾ':
            # ignore echo vowel after /ɾ/
            pass
        elif char in ignore:
            # ignore that which is to be ignored
            pass
        elif char in spaces:
            out+=' '
        elif char in phonet:
            index = phonet.index(char)
            out+=phonem[index]
        elif char in orth_nasal:
            index = orth_nasal.index(char)
            out+=phon_nasal[index]
        else:
            out+=char # otherwise, copy char as is
    return out

# replace nasal contours w/ underlying (simple) phoneme
# replace mid-high nasal vowels with mid-low
def ptp_fix_nasals(s):
    out=s
    for cn, sm in zip(conts, simps):
        if cn in out:
            out = out.replace(cn, sm)
    for k, v in mid.items():
        for x in v:
            if x in out:
                out=out.replace(x, k)
    return out

# replace allophones of ejective cons with underlying rep
def ptp_fix_ejects(s):
    out=s
    for k, v in eject.items():
        for alloph in v:
            if alloph in out:
                out = out.replace(alloph, k)
    return out
 
# mark vʔv sequences as v̰:
# add initial, medial glottal stop if applicable
def ptp_fix_lar(s):
    out=s
    for v in all_vowels:
        if v + 'ʔ' + v in out:
            out = out.replace(v+'ʔ'+v, v+'\u0330'+':')
    out = hiatus(out)
    temp = out.split(); out=''
    for sub in temp:
        if sub[0] in all_vowels:
            out+='ʔ'+sub+' '
        else:
            out+=sub+' '
    out=out.replace('\u0330\u0303','\u0303\u0330')
    return out.strip()
    
@ignore_null
# converts str in practical orth into phonemic   
def orth_to_work(orth_str):
    phon_str = orth_str;#print(phon_str)
    # simple 1-to-1 replacements
    phon_str = otw_replace(orth_str);#print('replace:',phon_str)
    phon_str = otw_mark_long(phon_str);#print('long:',phon_str)
    phon_str = hiatus(phon_str);#print('hiatus:',phon_str)
    phon_str = otw_mark_nasal(phon_str);#print('nasal:',phon_str)
    phon_str = otw_mark_lar(phon_str);#print('lar:',phon_str)
    
    phon_str = phon_str.replace('g', 'kʼ')
    phon_str = phon_str.replace('tʃ', 'tʃʼ')
    phon_str = 'ʔ' + phon_str if phon_str[0] in all_vowels else phon_str
    return phon_str

### helper methods for orth_to_work ###
    
# 1-1 replacements and excluded chars
def otw_replace(s):
    out=''
    # exclude chars in ignore
    for char in s:
        if char in ignore:
            pass
        elif char in spaces:
            out+=' '
        else:
            out+=char
    # orth to phon replacements
    for o, p in zip(all_orth, all_phon):
        if o in s:
            out = out.replace(o, p) # overpowered, please nerf
    return out
    

# inserts a glottal stop between dissimilar contiguous vowels
# and in vowel-initial words
def hiatus(s):
    out=''
    prev = ''
    # intervocalic
    for char in s:
        if char in all_vowels and prev in all_vowels:
            if char != prev:
                out+='ʔ'
        out+=char
        prev=char
    # word initial
    temp = out.split(); out=''
    for sub in temp:
        if sub[0] in all_vowels:
            out+='ʔ'+sub+' '
        else:
            out+=sub+' '
    return out.strip()

# marks nasalization at the end of each morpheme with a tilde
def otw_mark_nasal(s):
    prev=''
    folw=s[1] if len(s) > 1 else ''
    out=''
    for i, char in enumerate(s):
        folw=s[i+1] if len(s)>i+1 else ''
        if char in phon_v and prev in ('m', 'n') and folw != '\u0303':
            char = 'ɛ' if char == 'e' else char
            char = 'ɔ' if char == 'o' else char
            idx = phon_v.index(char)
            out += phon_nasal[idx]
        else:
            out+=char
        if char != '\u0330' and char != 'ʼ':
            prev=char
    
    return out

# replace all long vowels (marked orthographically as a geminate) vowel + :
# assumes nasalization markers have already been removed
def otw_mark_long(s):
    out=s   
    for v in all_vowels:
        if v+v in out:
            # long vowel spotted
            out=out.replace(v+v, v+':')
    return out

# replaces laryngeal vowel (marked w/ preceding apostrophe) with a laryngeal
# tilde underneath
def otw_mark_lar(s):
    out=''
    prev=''
    for i, char in enumerate(s):
        if prev in ('ʼ', "ʹ", "'") and char in all_vowels:
            out+=char+'\u0330'
        elif char in ('ʼ', "ʹ", "'"):
            pass
        else:
            out+=char
                
        prev=char
    out=out.replace('\u0330\u0303','\u0303\u0330')
    return out
        
if __name__ == '__main__':    
    main()