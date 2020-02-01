# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 07:02:18 2020

@author: marks
"""

import xml.etree.cElementTree as ET

root = ET.Element('água', ipa='agwɐ')
tree = ET.ElementTree(root)
tree.write('tmp.xml', encoding='utf8')
with open('tmp.xml', encoding='utf8') as f:
    for line in f:
        print(line)