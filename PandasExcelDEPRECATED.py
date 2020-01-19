# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 11:24:39 2019

Functions to help writing and reading pandas dataframes to csv's.
Specifically csv's that can be read using excel.

@author: Mark
"""

# adds utf-16 bom to first colname of dataframe
# because excel is stupid and expects a utf-16 bom
# in a utf-8 file
def add_bom(df):
    cols = df.columns
    first_col = cols[0]
    if '\uFEFF' not in first_col:
        first_col = '\uFEFF' + first_col
        cols = [first_col] + list(cols[1:])
    
    df.columns = cols

# removes utf-16 bom from first colname of dataframe
# because excel is stupid and expects a utf-16 bom
# in a utf-8 file 
def remove_bom(df):
    cols = df.columns
    first_col = cols[0]
    if first_col.startswith('\uFEFF'):
        first_col = first_col[1:]
        cols = [first_col] + list(cols[1:])
    
    df.columns = cols