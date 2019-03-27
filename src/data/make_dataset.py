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


def load_ebro(path, features, stations, variables, start, end):
    list_df = []
    for i_feature in features:
        feature = os.listdir(os.path.join(path, i_feature))

        for i_station in stations:
            station = [i for i in feature if i_station in i]

            for i_variable in variables:
                variable = [i for i in station if i_variable in i]

                if len(variable) > 0:
                    df = pd.read_csv(os.path.join(path, i_feature, variable[0]), sep = ';')

                    df.columns = df.columns.str.replace(' ', '')

                    df.FECHA = pd.to_datetime(df.FECHA)

                    df = df.set_index('FECHA')

                    # remove min and max dates
                    df = df.drop(df.filter(regex='FECHA').columns, axis=1)

                    # replace comma with dots
                    df = df.stack().str.replace(',','.').unstack()

                    #Text columns to numeric
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                    df = df.dropna(how='all', axis=1)

                    # complete hourly data
                    df = df.resample('H').ffill()/24

                    # Filter by period
                    df = df[(df.index >= start) & (df.index <= end)]

                    # add prefix to columns
                    prefix = variable[0].split('.')[0] + '_'
                    df = df.add_prefix(prefix)

                    # Append df to frames
                    list_df.append(df)

    # Concatenate frames into a single DataFrame
    df_ebro = pd.concat(list_df, axis=1)
    
    return df_ebro
        
        