# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 17:12:13 2020

@author: marks
"""

import datetime

date_str1 = '2019-01-14T03:46:55Z'
date1 = datetime.datetime.strptime(date_str1, '%Y-%m-%dT%H:%M:%SZ')

date_str2 = '2018-03-08T07:17:53Z'
date2 = datetime.datetime.strptime(date_str2, '%Y-%m-%dT%H:%M:%SZ')

print(date1)
print(date2)

assert date1 > date2
assert date2 < date1
