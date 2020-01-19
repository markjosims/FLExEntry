# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 16:59:12 2020

@author: marks
"""

import os
import shutil

wd = os.getcwd()
wd+='\\'

shutil.rmtree(wd+'subdir\\subsubdir')

os.mkdir(wd+'subdir\\subsubdir')