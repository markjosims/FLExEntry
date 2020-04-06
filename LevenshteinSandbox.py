# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 19:04:19 2019

@author: Mark
"""

import numpy as np

class SmartLevenshtein(object):
    
    def __init__(self):
        self.similar = {}
        self.weights = {}
        
    # set a unique weight for a character/set of characters
    # applies only for addition/subtraction
    # char is a str, and weight is an int or float
    # if str argument longer than one, each char is assigned weight
    def set_weight(self, char, weight):
        if type(char) is not str:
            raise TypeError('First argument must be str')
        if len(char) == 0:
            raise ValueError('First argument must have at least one character')
        if type(weight) is not int and type(weight) is not float:
            raise TypeError('Second argument must be int or float')
        for c in char:
            self.weights[c] = weight
    
    # set a subset of strings to be recognized as "similar"
    # (or dissimilar) and have a unique weight when one is
    # substituted for the other
    # string is a str of len > 1, and weight is an int or float
    def set_similar(self, string, weight):
        if type(string) is not str:
            raise TypeError('First argument must be str')
        if len(string) <= 1:
            raise ValueError('First argument must be more than a single character')
        if type(weight) is not int and type(weight) is not float:
            raise TypeError('Second argument must be int or float')
        self.similar[string] = weight

    def get_distance(self, s, t, ratio_calc=False):
        
        # Initialize matrix of zeros
        assert type(s) is str, s
        assert type(t) is str, t
        rows = len(s)+1
        cols = len(t)+1
        distance = np.zeros((rows,cols),dtype = float)
    
        # Populate matrix of zeros with the indices of each character of both strings
        for i in range(1, rows):
            distance[i][0] = i
        for k in range(1,cols):
                distance[0][k] = k
    
    
        # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
        for col in range(1, cols):
            for row in range(1, rows):
                # calculate cost for substitution
                if s[row-1] == t[col-1]:
                    sub_cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
                # check if chars are listed in dict of similar chars
                elif any(s[row-1] in k for k in self.similar.keys()):
                    sub_cost = 1 if not ratio_calc else 2
                    for k in self.similar.keys():
                        if s[row-1] in k and t[col-1] in k:
                            sub_cost = self.similar[k]
                else:
                    # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                    # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                    if ratio_calc == True:
                        sub_cost = 2
                    else:
                        sub_cost = 1
                    
                # calculate cost for deletion
                if s[row-1] in self.weights.keys():
                    del_cost = self.weights[s[row-1]]
                else:
                    del_cost = 1
                    
                # calculate cost for addition
                if t[col-1] in self.weights.keys():
                    add_cost = self.weights[t[col-1]]
                else:
                    add_cost = 1
                        
                distance[row][col] = min(distance[row-1][col] + del_cost,
                                     distance[row][col-1] + add_cost,
                                     distance[row-1][col-1] + sub_cost)
        if ratio_calc == True:
            # Computation of the Levenshtein Distance Ratio
            Ratio = ((len(s)+len(t)) - distance[rows-1][cols-1]) / (len(s)+len(t))
            # print(distance)
            return Ratio
        else:
            # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
            # insertions and/or substitutions
            # This is the minimum number of edits needed to convert string a to string b
            return distance[rows-1][cols-1]
            
lev = SmartLevenshtein()