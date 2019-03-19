#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 08:12:26 2019

@author: miguelcaballero
"""

# STD lib imports
import os
import sys

# Third party libs
import numpy as np
import pandas as pd


def delta_height(data, cols, hrs, norm=True):
    '''
    Create the change in stage
    '''
    list_d = []
    for col in cols:
        if norm:
            delta = (data[col].shift(hrs) - data[col])/hrs
        else:
            delta = data[col].shift(hrs) - data[col]
        
        name = 'delta_{}_{}'.format(hrs, col)
        data[name] = delta
        
    # remove rows
    data = data.iloc[hrs:, :]
        
    return data


def shift_columns(data, cols, hrs):
    '''
    #number of derived columns per feature
    # time delta in hr 
    '''
    for col in cols:  
        for h in range(1, hrs + 1):
            delta = data[col].shift(h).fillna(0).values
            name = 'shift_{}_{}'.format(col, h)
            data[name] = delta
            
    return data
                     
