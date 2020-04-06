# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 08:27:37 2020

@author: marks
"""

import xml.etree.cElementTree as ET
import lxml.etree as etree

in_file = 'Flexport_3_26//Flexport_3_26.lift'
out_file = 'Flexport_3_26//SilFieldsMerged.lift'

def main():
    tree = ET.parse(in_file)
    root = tree.getroot()
    for elem in root:
        deprecated_field, dep_i = None, None
        new_field, new_i = None, None
        for i, field in enumerate(elem.findall('field')):
            # set text language to Nadëb
            form = field.find('form')
            form.set('lang', 'mbj')
            
            _, text = read_form(form)
            field_type = field.get('type')

            if field_type == 'Sil Dict 2011':
                deprecated_field, dep_i = text, i
            elif field_type == 'SIL Dict 2011':
                new_field, new_i = text, i
        if deprecated_field:
            new_field = f"{deprecated_field}, {new_field}" if new_field else deprecated_field
            if new_i:
                elem.findall('field')[new_i].text = new_field
            else:
                ET.SubElement(elem, 'field', type='SIL Dict 2011')
            elem.remove( elem.findall('field')[dep_i] )



    tree.write(out_file, encoding='utf8')
    
    
    file = etree.parse(out_file)
    out = etree.tostring(file, pretty_print=True, encoding='unicode')
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        f.write(out)


# reads all <form> tags under a given element
# returns a dictionary with the language for each form
# as keys, and the text of each form as values
def read_all_forms(elem):
    out = {}
    forms = elem.findall('form')
    for f in forms:
        lang, text = read_form(f)
        # assuming one form per lang per parent element
        assert lang not in out
        out[lang] = text
    return out
    
# gets lang attr from a form tag
# and reads all text from a text child elements
def read_form(form):
    lang = form.get('lang')
    text = form.findall('text')
    text = [get_elem_text(x) for x in text]
    text = text[0] if len(text) == 1 else text
    
    return lang, text

def get_elem_text(elem):
    out = elem.text if elem.text else ''
    for span in elem.findall('span'):
        if span.text:
            out += span.text
        if span.tail:
            out += span.tail
    return out

if __name__ == '__main__':
    main()