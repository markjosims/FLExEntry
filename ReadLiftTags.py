# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 21:10:45 2019

@author: Mark
"""

import re

re_span = re.compile(r"</?span( lang='(en|pt|mbj)')?>")
re_form = re.compile(r"</?form( lang='(en|pt|mbj)')?>")
re_text = re.compile(r'</?text[^>]*?>')
re_gloss = re.compile(r"</?gloss( lang='(en|pt|mbj)')?>")
re_rev = re.compile(r"</?reversal type='(en|pt|mbj)'>")

        
def tag_globals():
    global entry_tags, entry_keys, sense_tags, sense_keys
    entry_tags = {'<pronunciation':read_pronunciation,
                  '<note':read_note,
                  '<relation type':read_variant,
                  '<lexical-unit>':read_lu,
                  '<sense':read_sense_wrapper,
                  "<trait  name='morph-type'":read_morph_type
                  }
    entry_keys =   {'dateModified':'date',
                    '<pronunciation':'pronunciation',
                    '<note':'note',
                    '<relation type':'variant',
                    '<lexical-unit>':'headword',
                    '<sense':'sense',
                    "<trait  name='morph-type'":'morph_type'
                    }
    sense_tags = {'<definition>':read_definition,
                  '<grammatical-info':read_pos,
                  '<note':read_note,
                  '<gloss':read_gloss,
                  '<reversal type':read_reversal
                  }
    sense_keys = {'<definition>':'def',
                  '<grammatical-info':'pos',
                  '<note':'note',
                  '<gloss':'gloss',
                  '<reversal type':'reverse'
                  }

def read_entry(r, id_only=False):
    open_tag = read_decode(r)
    assert open_tag.startswith('<entry')
    
    entry_id = get_xml_kwarg(open_tag, 'id')
    if not id_only:
        entry_data = {k:None for k in entry_keys.values()}
        entry_data['note'] = []
        entry_data['sense'] = []
        entry_data['variant'] = {}
        entry_data['entry_id'] = entry_id
        entry_data['date'] = get_xml_kwarg(open_tag, 'dateCreated')
    
    line, line_bytes = r_d_bytes(r)
    while True:
        for tag, funct in entry_tags.items():
            if line.startswith(tag):
                step_back(r, line_bytes)
                key = entry_keys[tag]
                data = funct(r)
                if not id_only:
                    if key in ('note', 'sense'):
                        entry_data[key].append(data)
                    elif key == 'variant':
                        entry_data[key][data[0]] = data[1] if len(data) == 2 else data[1:]
                    else:
                        assert not entry_data[key]
                        entry_data[key] = data
                break
        else:
            assert line == '</entry>', line
            break
        
        line, line_bytes = r_d_bytes(r)
    if id_only:
        return entry_id
    entry_data = {k:(v if v else None) for k, v in entry_data.items()}
    headword = entry_data['headword']
    headword = ' '+headword if headword.startswith('=') else headword
    entry_data['headword'] = headword
    return entry_data

def read_sense(r, id_only=False):
    open_tag = read_decode(r)
    assert open_tag.startswith('<sense')
    
    sense_id = get_xml_kwarg(open_tag, 'id')
    if not id_only:
        sense_data = {k:None for k in sense_keys.values()}
        sense_data['reverse'] = []
        sense_data['sense_id'] = sense_id
    line, line_bytes = r_d_bytes(r)
    while True:
        for tag, funct in sense_tags.items():
            if line.startswith(tag):
                step_back(r, line_bytes)
                key = sense_keys[tag]
                data = funct(r)
                if not id_only:
                    if key == 'reverse':
                        sense_data[key].append(data)
                    else:
                        assert not sense_data[key]
                        sense_data[key] = data
                break
        else:
            # if current line did not match any tags
            # end of sense
            assert line == '</sense>', line
            break
        
        line, line_bytes = r_d_bytes(r)
        
    if id_only:
        return sense_id
    sense_data = {k:(v if v else None) for k, v in sense_data.items()}
    return sense_data

def read_sense_wrapper(r):
    return read_sense(r, id_only=True)

def read_pronunciation(r):
    open_tag = read_decode(r)
    assert open_tag == '<pronunciation>'
    s = read_decode(r)
    s = read_form(s)
    end_tag = read_decode(r)
    assert end_tag == '</pronunciation>'
    return s

def read_definition(r):
    open_tag = read_decode(r)
    assert open_tag == '<definition>'
    # definition can frame multiple arguments
    # for multiple languages
    # save all to dict
    this_def = {}
    s = read_decode(r)
    while s != '</definition>':
        lang = get_xml_kwarg(s, 'lang')
        assert lang not in this_def.keys(), lang
        def_str = read_form(s)
        this_def[lang] = def_str
        s = read_decode(r)
    return this_def

def read_variant(r):
    ref_tag = read_decode(r)
    ref = get_xml_kwarg(ref_tag, 'ref')
    values = []
    line = read_decode(r)
    while line.startswith('<trait '):
        assert get_xml_kwarg(line, 'name') in ('variant-type', 'complex-form-type', 'is-primary'), get_xml_kwarg(line, 'name')
        values.append( get_xml_kwarg(line, 'value') )
        line = read_decode(r)
    summ = None
    if line == "<field type='summary'>":
       summ = read_decode(r)
       summ = read_form(summ)
       end_tag = read_decode(r)
       assert end_tag == '</field>'
       line = read_decode(r)
    assert line == '</relation>', line + ' ' + ref_tag
    if summ:
        return (ref, *values, summ)
    else:
        return (ref, *values)

def read_note(r):
    type_str = read_decode(r)
    if type_str == '<note>':
        note_type = ''
    else:
        note_type = get_xml_kwarg(type_str, 'type')
    notes = []
    s = read_decode(r)
    while s.startswith('<form '):
        notes.append(read_form(s))
        s = read_decode(r)
    end_tag = s
    assert end_tag == '</note>'
    return (*notes, note_type)
        
def read_span(s):
    s = re_span.sub("", s)
    assert 'span>' not in s, s
    return s

def read_form(s):
    s = read_span(s)
    s = re_form.sub("", s)
    s = read_text(s)
    assert 'form>' not in s, s
    return s.strip()

def read_gloss(r):
    glosses = {}
    line, line_bytes = r_d_bytes(r)
    while line.startswith('<gloss'):
        this_gloss, lang = get_gloss(line)
        assert lang not in glosses
        glosses[lang] = this_gloss
        
        line, line_bytes = r_d_bytes(r)
    step_back(r, line_bytes)
    return glosses
    
def get_gloss(s):
    lang = get_xml_kwarg(s, 'lang')
    assert lang in ('pt', 'en'), lang
    s = read_span(s)
    s = re_gloss.sub("", s)
    s = read_text(s)
    assert 'gloss>' not in s
    return (s.strip(), lang)

def read_reversal(r):
    s = read_decode(r)
    lang = get_xml_kwarg(s, 'lang')
    assert lang in ('pt', 'en'), lang
    s = read_span(s)
    s = re_rev.sub("", s)
    s = read_form(s)
    assert '<reversal' not in s
    end_tag = read_decode(r)
    assert end_tag == '</reversal>'
    return (s.strip(), lang)

def read_text(s):
    s = re_text.sub("", s)
    assert 'text>' not in s
    return s.strip()

def read_lu(r):
    open_tag = read_decode(r)
    assert open_tag == '<lexical-unit>', open_tag
    s = read_decode(r)
    lang = get_xml_kwarg(s, 'lang')
    assert lang == 'mbj', lang
    s = read_form(s)
    end_tag = read_decode(r)
    assert end_tag == '</lexical-unit>', end_tag
    return s.strip()
    
def read_morph_type(r):
    s = read_decode(r)
    assert get_xml_kwarg(s, 'name') == 'morph-type'
    return get_xml_kwarg(s, 'value')

def read_pos(r):
    s = read_decode(r)
    end_tag = read_decode(r)
    assert end_tag == '</grammatical-info>'
    return get_xml_kwarg(s, 'value')

def read_decode(r):
    line = r.readline()
    line = line.decode('utf8')
    line = line.replace(',',';')
    line = line.replace('"', "'")
    line = line.strip()
    return line

def r_d_bytes(r):
    these_bytes = r.readline()
    line = these_bytes.decode('utf8')
    line = line.replace(',',';')
    line = line.replace('"', "'")
    line = line.strip()
    return line, these_bytes

def step_back(r, line_bytes):
    offset = len(line_bytes) * -1
    r.seek(offset, 1)

def get_xml_kwarg(s, label):
    split = s.split(sep="'")
    kwarg_found = False
    for chunk in split:
        if kwarg_found:
            return chunk
        elif chunk.endswith(label+'='):
            kwarg_found = True
    else:
        raise ValueError(f'No kwarg matching label {label} in string {s}.')

tag_globals()