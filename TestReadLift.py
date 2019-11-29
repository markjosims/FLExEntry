# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 18:36:17 2019

@author: Mark
"""

from unittest import main, TestCase
from io import StringIO
from ReadLift import read_span, read_form, read_gloss, read_lu, read_morph_type,\
read_pos, read_reversal, read_pronunciation, read_definition, read_note


class TestReadLift(TestCase):
    def test1_span(self):
        s = r'<form lang="en"><text> F<span lang="pt">ieldnotes Epps</span>/<span lang="pt">Obert</span>, 2018</text></form>'+'\n'
        out = r'<form lang="en"><text> Fieldnotes Epps/Obert, 2018</text></form>'+'\n'
        self.assertEqual(out, read_span(s))
        
    def test2_form(self):
        s = r'<form lang="pt"><text><span lang="en">passaro (generico)</span></text></form>'+'\n'
        out = 'passaro (generico)'
        self.assertEqual(out, read_form(s))
        
    def test3_gloss(self):
        s = r'<gloss lang="en"><text>shoulder</text></gloss>'+'\n'
        out = ('shoulder', 'en')
        self.assertEqual(out, read_gloss(s))
        
    def test4_lu(self):
        r = StringIO('<lexical-unit>\n'+
                   '<form lang="mbj"><text>p’aa hẽnh</text></form>\n'+
                   '</lexical-unit>\n')
        out = 'p’aa hẽnh'
        self.assertEqual(out, read_lu(r))
    
    def test5_morph_type(self):
        s = '<trait  name="morph-type" value="phrase"/>\n'
        out = "phrase"
        self.assertEqual(out, read_morph_type(s))
        
    def test6_pos(self):
        r = StringIO('<grammatical-info value="Noun">\n</grammatical-info>\n')
        out = 'Noun'
        self.assertEqual(out, read_pos(r))
        
    def test7_rev(self):
        r = StringIO('<reversal type="pt"><form lang="pt"><text>breu</text></form>\n</reversal>\n')
        out = ('breu', 'pt')
        self.assertEqual(out, read_reversal(r))
        
    def test8_pronunc(self):
        r = StringIO('<pronunciation>\n<form lang="mbj"><text>kajaɾɛ̃:</text></form>\n</pronunciation>\n')
        out = 'kajaɾɛ̃:'
        self.assertEqual(out, read_pronunciation(r))
        
    def test9_def(self):
        r = StringIO('<definition>\n<form lang="en"><text>paddle; oar</text></form>\n<form lang="pt"><text>remo</text></form>\n</definition>\n')
        out = {'pt':'remo','en':'paddle; oar'}
        self.assertEqual(out, read_definition(r))
        
    def testa_note(self):
        r = StringIO('<note type="bibliography">\n<form lang="pt"><text><span lang="en">Weir 1986, Weir 1990</span></text></form>\n</note>\n')
        out = ('Weir 1986, Weir 1990', 'bibliography')
        self.assertEqual(out, read_note(r))
        
    def testb_note(self):
        r = StringIO('<note>\n<form lang="pt"><text>great-granddaughter= tatatoog</text></form>\n</note>\n')
        out = ('great-granddaughter= tatatoog', '')
        self.assertEqual(out, read_note(r))
    
if __name__ == '__main__':
    main()