# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 23:18:02 2020

@author: marks
"""

from xml.dom import minidom

lift = minidom.parse('TestExport.lift')
entries=lift.getElementsByTagName('entry')

print(entries[0].attributes['id'].value)
print(entries[0].childNodes[1])

import xml.etree.ElementTree as ET

tree = ET.parse('TestExport.lift')
root = tree.getroot()

print(len(root))
for elem in root:
    print(f'**{elem}')
    print(f'***{len(elem)}')
    for subelem in elem:
        print(f'\t**{subelem}')
        print(f'\t{subelem.attrib}')
        for subsubelem in subelem:
            print(f'\t\t**{subsubelem}')
            print(f'\t\t**{subsubelem.attrib}')
            print(f'\t\t**{subsubelem.text}')