con_ipa = ("m", "n", "ɲ", "ŋ", "p", "t", "k", "b", "d", "ɟ", "g", "ʃ", "h", "w", "ɾ", "j", "ʔ")
con_working = ("m", "n", "nh", "ng", "p", "t", "k", "b", "d", "ts", "g", "s", "h", "w", "r", "j")
vowels_ipa = ("i", "ɨ", "u", "e", "ə", "o", "ɛ", "ʌ", "ɔ", "a", "ə", "ɛ", "ʌ", "ɔ")
vowels_working = ("i", "y", "u", "e", "ë", "o", "é", "ä", "ó", "a", "ë", "é", "ä", "ó")
port = ('c', 'f', 'l', 'q', 'v', 'z', 'x')

global lexemes, phonetics

lexemes = []
phonetics = []

# read every line in file containing input lexemes
# write apostrophe as 'x' after a consonant (indicating laryngealization)
# remove all other punctuation
def read_lexemes(filename):
    in_file = open(filename, 'r', encoding='utf8')
    for line in in_file:
        this_lexeme = remove_gloss(line)
        this_lexeme = remove_punct(this_lexeme)
        #print("w/ punct:", line) #-debugging
        #print("w/o punct:", this_lexeme) #-debugging
        if (this_lexeme != None) and (this_lexeme.strip() != ''):
            lexemes.append(this_lexeme.strip())
    in_file.close()

# feeds single string
# returns string w/o punctuation
# and w/ laryngeal apostrophe replace_listd w/ 'x'
# return fed string if <= 1 char
def remove_punct(line):
    punct = ("\u2018", "\u2019", "\'", '\"', '\u201c', '\u201d', ".", "?", ",", "(", ")", "[", "]", ";", ":",
             '-', '_', '\\', '/', '\ufeff')
    line = line.strip()
    if len(line) <= 1:
        if line in punct:
            return
        return line
    this_lexeme = ""
    next_char = line[1]
    prev = ''
    for i in range(len(line)):
        char = line[i]
        # check if char is apostrophe, if so, check if indicates laryngeal
        if char in ("\u2018", "\u2019", "\'"):
            if (prev in con_working) and (next_char in vowels_working):
                # apostrophe is laryngeal, rewrite as 'x'
                this_lexeme += 'x'

        # check if char is other punctuation
        elif char in punct:
            this_lexeme += ' '

        # otherwise, copy as is
        else:
            this_lexeme += char

        prev = char
        if i+2 < len(line):
            next_char = line[i+2]
        else:
            next_char = ''
    return this_lexeme

# reads lexeme entry token-by-token
# looks for tell-tale signs of non-nadeb morphemes
# returns string w/all tokens not bearing red flags
def remove_gloss(line):
    if line == None:
        return
    digph = ('nh', 'ng', 'ts')
    line = line.split(sep=' ')
    new_line = ""
    for token in line:
        if (len(token) < 1) or (token == ' '):
            continue
        prev = ''
        discard = False
        for char in token:
            # if non-nadeb char is found, discard
            if char in port:
                discard = True
                break
            # if two contiguous consonants found, discard
            elif (prev in con_working) and (char in con_working) and (prev+char not in digph):
                discard = True
                break
            else:
                prev = char
        if discard:
            continue
        else:
            new_line += token + ' '
    return new_line

# iterates thru every item contained in lexemes
# replaces all digraphs and chars w/ diacritics with
# ipa equivalents before ipa_subs is called
def digraphs_and_diac():
    cons = ('nh', 'ng', 'ts')
    diac = ('\u0301', '\u0308')
    for i in range(len(lexemes)):
        entry = lexemes[i]
        new_lexeme = ""
        prev = ''
        for char in entry:
            # if last two chars read correspond to nasal digraph
            if (prev+char in cons):
                idx = con_working.index(prev+char)
                # delete last char added to pending entry
                new_lexeme = new_lexeme[:-1]
                # add appropriate ipa value
                new_lexeme += con_ipa[idx]
            elif (char in diac):
                #print("DIACRITIC FOUND")
                idx = vowels_working.index(prev+char)
                # delete last char added to pending entry
                new_lexeme = new_lexeme[:-1]
                # add appropriate ipa value
                new_lexeme += vowels_ipa[idx]
            else:
                new_lexeme += char
            prev = char

        phonetics.append(new_lexeme)


# iterates thru every item contained in lexemes
# does simple character-for-character substitutions to ipa equivalent
# outputs equivalent into phonetics global list
def ipa_subs():
    for i in range(len(phonetics)):
        entry = phonetics[i]
        this_phon = ""
        for char in entry:
            # check if current char is consonant
            if char in con_working:
                idx = con_working.index(char)
                this_phon += con_ipa[idx]
            # check if current char is vowel
            elif char in vowels_working:
                idx = vowels_working.index(char)
                this_phon += vowels_ipa[idx]
            # else copy as is
            else:
                this_phon += char
        phonetics[i] = this_phon

# inserts a tilde on vowels following
# a nasal segment
def nasal_allos():
    for i in range(len(phonetics)):
        entry = phonetics[i]
        new_phon = ""
        nasals = ('m', 'n', 'ɲ', 'ŋ')
        nasal = False
        prev = ''
        for j in range(len(entry)):
            char = entry[j]
            if nasal:
                # check for long vowel
                if (prev in vowels_ipa) and (char in vowels_ipa):
                    if char == prev:
                        new_phon += char+'\u0303'
                    # if hiatus, don't add nasal
                    else:
                        new_phon += char
                        nasal = False
                elif char in vowels_ipa:
                    new_phon += char+'\u0303'
                # don't reset marker if found nasal con
                elif char in nasals:
                    new_phon += char
                # don't add redundant nasal markers
                elif char == '\u0303':
                    nasal = False
                else:
                    new_phon += char
                    nasal = False
            elif char in nasals:
                nasal = True
                new_phon += char
            else:
                new_phon += char
            prev = char
        phonetics[i] = new_phon

# epenthesizes oral stops before nasals
# preceded by oral vowels
def nasal_contours():
    nasals = ('m', 'n', 'ɲ', 'ŋ')
    orals = ('b', 'd', 'ɟ', 'g')
    for i in range(len(phonetics)):
        entry = phonetics[i]
        new_phon = ""
        prev = ''
        for j in range(len(entry)):
            char = entry[j]
            # nasal consonant following oral vowel
            if (char in nasals) and (prev in vowels_ipa):
                idx = nasals.index(char)
                new_phon += orals[idx]+nasals[idx]
            # otherwise, copy as is
            else:
                new_phon += char
            prev = char
        phonetics[i] = new_phon

# iterates thru all items in phonetics
# identifies sequences of identical vowels
# replaces second vowel w/ ':' to mark length
def long_vowels():
    for i in range(len(phonetics)):
        entry = phonetics[i]
        new_phon = ""
        prev = ''
        for char in entry:
            # vowel is same as previous, add length marker
            if (char in vowels_ipa) and (char == prev):
                new_phon += ':'
            # otherwise, copy as is
            else:
                new_phon += char
            prev = char
        phonetics[i] = new_phon

# functions same as long_vowels, except except
# searches for nasal tilde
def long_nasal_vowels():
    for i in range(len(phonetics)):
        entry = phonetics[i]
        # skip if entry is 1 char or less
        if len(entry) <= 1:
            continue

        new_phon = ""
        prev = ''
        next_char = entry[1]
        nasal = False
        skip = False
        for j in range(len(entry)):
            # colon inserted last run, skip nasal diacritic this run
            if skip:
                skip = False
                continue
            char = entry[j]
            # char is nasal diacritic, set markers & move on
            if char == '\u0303':
                nasal = True
                prev += char
                new_phon += char

            # found diacritic in last pass
            elif nasal:
                #print('prev: {p}, char+next_char: {c}'.format(p=prev, c=char+next_char))#-debugging
                # check for two identical vowels w/ tildes
                if char+next_char == prev:
                    #print("long nasal detected") #-debugging
                    new_phon += ':'
                    skip = True
                # check for two identical vowels, tilde on first
                elif char == prev[0]:
                    #print("long nasal w/ 1 tilde detected") #-debugging
                    new_phon += ':'
                else:
                    new_phon += char
                # update markers
                nasal = False
                prev = char

            # otherwise copy char as is
            else:
                new_phon += char
                prev = char
            # update next_char
            if j+2 < len(entry):
                next_char = entry[j+2]
            else:
                next_char = ''
        phonetics[i] = new_phon

# iterate thru all items in phonetics
# epenthesizes glottal stops into empty
# onsets and codas
def glottal_stops():
    for i in range(len(phonetics)):
        entry = phonetics[i]

        # special case, entry is only 1 char
        if len(entry) <= 1:
            if entry in vowels_ipa:
                phonetics[i] = 'ʔ' + entry + 'ʔ'
            continue

        new_phon = ""
        prev = ''
        next_char = entry[1]

        for j in range(len(entry)):
            char = entry[j]
            #print("entry: {e}, new_phone: {n}".format(e=entry, n=new_phon))#-debugging
            if char in vowels_ipa:
                # word initial
                if (prev in ('', ' ')):
                    #print("char {c} is vowel, found after pause {p}".format(c=char, p=prev))#-debugging
                    new_phon += 'ʔ'
                # hiatus
                elif (prev in vowels_ipa) or (prev == '\u0303') or (prev == ':'):
                    #print("char {c} is vowel, found after hiatus {p}".format(c=char, p=prev))#-debugging
                    new_phon += 'ʔ'

            new_phon += char

            # update prev
            prev = char

            # empty coda
            if (char in vowels_ipa or char == ':' or char == '\u0303') and (next_char in ('', ' ')):
                #print("char {c} is vowel, found before pause {n}".format(c=char, n=next_char))#-debugging
                new_phon += 'ʔ'
                prev = 'ʔ'

            # update next_char
            if j+2 < len(entry):
                next_char = entry[j+2]
                #print('next_char set to [j+2]:', next_char)#-debugging
            else:
                next_char = ''

        # update entry
        phonetics[i] = new_phon

# rewrites the non-tenuis dorsal stops
# to reflect their positional allophones
def ejectives():
    voiced = ('ɟ', 'g') # used here as underlying symbol
    interv = ('ʔtʃ', 'ʔk') # intervocalic allophone
    onset = ("tʃ\'", "k\'") # allophone as onset
    for i in range(len(phonetics)):
        entry = phonetics[i]

        # special case, if entry <=1 char, ignore
        if len(entry) <= 1:
            continue

        new_phon = ""
        prev = ''
        next_char = entry[1]
        for j in range(len(entry)):
            char = entry[j]
            if char in voiced: # consonant found, discern environment
                idx = voiced.index(char)
                if prev in ('', ' '):
                    new_phon += onset[idx]
                elif (prev in vowels_ipa) and (next_char in vowels_ipa):
                    new_phon += interv[idx]
                else:
                    new_phon += voiced[idx]
            else:
                new_phon += char

            # update pointers
            prev = char
            if j+2 < len(entry):
                next_char = entry[j+2]
            else:
                next_char = ''
        phonetics[i] = new_phon

# adds nonreleased diacritic after coda plosives
# and a superscript schwa after coda /ɾ/
def coda():
    plosives = ['p', 't', 'k', 'b', 'd', 'ɟ', 'g']
    for i in range(len(phonetics)):
        entry = phonetics[i]

        # special case: if entry is <=1 char, ignore
        if len(entry) <= 1:
            continue

        next = entry[1]
        new_phon = ''
        for j in range(len(entry)):
            char = entry[j]
            if (char in plosives) and (next in ('', ' ')):
                new_phon += char+'\u031a'
            elif (char == 'ɾ') and (next in ('', ' ')):
                new_phon += char+'\u1d4a'
            else:
                new_phon += char

            # update next
            if j+2 < len(entry):
                next = entry[j+2]
            else:
                next = ''
        phonetics[i] = new_phon

# rewrites laryngeal 'x' as appropriate
# diacritic under vowel
def laryngeals():
    for i in range(len(phonetics)):
        entry = phonetics[i]
        new_phon = ""
        laryng = False
        prev=''
        skip=False
        for j in range(len(entry)):
            if skip:
                skip = False
                continue

            char = entry[j]
            if char == 'x':
                prev = 'x'
                continue
            if prev == 'x':
                new_phon += char
                laryng = True
            elif laryng:
                if char == ':':
                    new_phon += 'ʔ' + prev
                elif char == '\u0303':
                    new_phon += '\u0303'+'ʔ'+prev+'\u0303'
                    skip=True
                laryng = False
            else:
                new_phon += char
            prev=char
        phonetics[i] = new_phon


# iterates thru lexemes
# splits lexemes into tokens
# asks user which to discard, which to change
# and which to keep
# skips junk
### DUE TO CHANGES IN READ LEXEMES SHOULD NO LONGER BE NECESSARY ###
def review():
    global phonetics
    # split lexeme entries into tokens, strip spaces
    # remove empty tokens and entries
    replace_list = []
    for i in range(len(phonetics)):
        entry = phonetics[i].strip().split(sep=' ')
        for token in entry[:]:
            if len(token) == 0:
                entry.remove(token)
        if len(entry) != 0:
            replace_list.append(entry)
    phonetics = replace_list

    # iterate thru new list
    for i in range(len(phonetics)):
        entry = phonetics[i]
        if len(entry) <= 1:
            phonetics[i] = entry[0]
            print("Entry:", phonetics[i])
            continue
        print("Entry:", entry)
        new_entry = ''
        for token in entry:
            print("Token:", token)
            keep = input("Keep? y/n: ")
            if keep.upper() == 'Y':
                new_entry += token.strip() + ' '
        print(new_entry)
        phonetics[i] = new_entry


def main():
    read_lexemes("C:\\Users\\Mark\\Desktop\\lexemes_final_list.txt")
    digraphs_and_diac()
    ipa_subs()
    nasal_allos()
    nasal_contours()
    long_vowels()
    long_nasal_vowels()
    glottal_stops()
    ejectives()
    coda()
    laryngeals()
    out_file = open("C:\\Users\\Mark\\Desktop\\ipa_con_out.csv", 'w', encoding='utf8')
    out_file.write('\ufeff')
    for i in range(len(lexemes)):
        print("lex:", lexemes[i])
        print("phon:", phonetics[i])
        out_file.write(lexemes[i]+",["+phonetics[i]+"]\n")

main()