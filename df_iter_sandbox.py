# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 21:13:31 2019

@author: marks
"""

from time import time
import pandas as pd

df = pd.DataFrame()
df['c1'] = [0 for i in range(10000)]
df['c2'] = [0 for i in range(10000)]
df['c3'] = [0 for i in range(9999)] + [1]


def time_exec(f):
    def g():
        start = time()
        f()
        end = time()
        print(str(f), end-start)
    return g

@time_exec
def listcomp():
    for i in range(50):
        c3 = df['c3']
        is1 = [n == 1 for n in c3]
        index = is1.index(True)

@time_exec
def pd_iterrows():
    for i in range(50):
        for index, row in df.iterrows():
            if row['c3'] != 1:
                continue
            return
    
listcomp()
pd_iterrows()