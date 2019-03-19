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

    
def load_data(path, raw_file):
    '''
    Function to load the raw data from ITA
    '''
    path_file = os.path.join(path, raw_file)
    data = pd.read_csv(path_file, 
                       parse_dates = ['time'], 
                       index_col = 'time')
    
    return data


def load_meteo(path, dic_files, cols):
    '''
    Load a list of meteorogical data anc concatenate
    '''
    list_df = []
    for i, f in dic_files.items():
        #  Read csv into a DataFrame: df
        path_file = os.path.join(path, f)
        df = pd.read_csv(path_file, 
                         sep = ';', 
                         usecols = cols, 
                         parse_dates = ['FECHA'], 
                         index_col = 'FECHA')
        
        # rename columns
        colnames = ['{}_{}'.format(x, i) for x in cols if x != 'FECHA']
        df.columns = colnames
        
        # Append df to frames
        list_df.append(df)
        
    # Concatenate frames into a single DataFrame
    df_meteo = pd.concat(list_df, axis=1)
    
    # Fill nan with zeros
    #df_meteo.fillna(value = 0, inplace=True)
    df_meteo.replace(to_replace=['Ip','Acum'] , value=0, inplace=True)

    #Text columns to numeric
    for col in df_meteo.columns:
        df_meteo[col] = pd.to_numeric(df_meteo[col], errors='coerce')
    
    return df_meteo
        
        
        
        
        
        