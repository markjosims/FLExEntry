# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 19:58:52 2019

@author: Mark
"""

in_file = 'entries/agëëm.json'

def main():
    with open(in_file, 'rb') as f:
        for line in f:
            print(line.decode('unicode_escape'))

if __name__ == '__main__':
    main()