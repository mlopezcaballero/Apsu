# STD lib imports
import os
import sys

# Third party libs
import numpy as np
import pandas as pd

# sklear stuff
from sklearn.externals import joblib

# Tensorflow stuff
import keras

import warnings
warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


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


def delta_height(data, cols, hrs, norm=True):
    '''
    Create the change in stage
    '''
    list_d = []
    for col in cols:
        if norm:
            delta = (data[col].shift(hrs).fillna(method='backfill') - data[col])/hrs
        else:
            delta = data[col].shift(hrs).fillna(method='backfill') - data[col]
        
        name = 'delta_{}_{}'.format(hrs, col)
        data[name] = delta
        
    # remove rows
    data = data.iloc[hrs:, :]
        
    return data


def column_shift(df, dup_cols, N, delta): 
    '''
    Deriving new features by shifting columns by a given timedelta. That is, each time series 
    is shifted back N*delta, N*2*delta, N*3*delta, where N is number of columns and delta
    time shift periods.
    '''    
    for col in dup_cols:
        for i in range (1,N+1):
            colname = col + "_" + str(i*delta)
            df[colname] = df[col].shift(periods = i*delta).fillna(method='backfill')
            
    return df


def main(raw_file):
    # Load data from ITA
    path = 'ENTRADA/'
    df_raw = load_data(path, raw_file)

    # Drop Grisen and RIESGO base on previous data exploration
    df_raw = df_raw.drop(['GRISEN_NR'], axis=1)
    df_raw = df_raw.drop(['RIESGO'], axis=1)

    # period of the data
    start = df_raw.index.min()
    end = df_raw.index.max()

    idx = df_raw.resample('D').mean().index

    # Estation to load data
    estaciones = {'pna': '9262-19530901-20190131.csv',  
                  'zar_aero':'9434-19410101-20190302.csv'}

    # inputs
    cols = ['FECHA','TMEDIA','TMIN','TMAX','PRECIPITACION']
    path_meteo = 'data/AEMET/DatosPorEstacion/'

    # Load meteo data and filter by period
    df_meteo = load_meteo(path_meteo, estaciones, cols) 

    # complete hourly data
    df_meteo = df_meteo.resample('H').ffill()/24

    # Filter by period
    df_meteo = df_meteo[(df_meteo.index >= start) & (df_meteo.index <= end)]

    # Load data from SAHIEBRO
    path_ebro = 'data/SAIHEBRO/'
    features = ['AFORO', 'PRECIPITACION', 'TEMPERATURA']
    stations = ['A001', 'A002', 'A005', 'A011', 'EM75']
    variables = ['NRIO1', 'PACUM', 'TEMPE']

    df_ebro = load_ebro(path_ebro, features, stations, variables, start, end)

    # Concatenate both data frames
    df = pd.concat([df_raw, df_meteo, df_ebro], axis=1)

    # Features
    columns_y = ['pred_24h', 'pred_48h', 'pred_72h']
    columns_x = [x for x in df.columns if x not in columns_y]

    X = df[columns_x]
    Y = df[columns_y]

    # Create features base on delta to time
    cols_delt = ['ALAGON_NR', 'NOVILLAS_NR', 'TAUSTE_NR', 'TUDELA_NR', 'ZGZ_NR']
    X = delta_height(X, cols_delt, 1, True)
    X = delta_height(X, cols_delt, 5, True)

    # number of derived columns per feature
    N = 1  

    # time delta in hr
    delta = [8, 145]

    # Create new shifted features
    dup_cols = ['TUDELA_NR', 'NOVILLAS_NR']
    X = column_shift(X, dup_cols, N, delta[0])

    dup_cols = ['ALAGON_NR', 'ZGZ_NR']
    X = column_shift(X, dup_cols, N, delta[1])

    print(X.isnull().sum())
    
    X = X.fillna(method='backfill')
    X = X.fillna(method='ffill')
    #X = X.dropna()
    
    print(X.isnull().sum())

    scaler = joblib.load('data/interim/scaler.pkl')
    columnas = X.columns
    indices = X.index
    X = scaler.transform(X)
    X = pd.DataFrame(X, columns=columnas, index=indices)

    #Predictions
    model_24 = keras.models.load_model('data/interim/model_1_24h.h5')
    model_48 = keras.models.load_model('data/interim/model_1_48h.h5')
    model_72 = keras.models.load_model('data/interim/model_1_72h.h5')

    predictions_24 = model_24.predict(X)
    predictions_48 = model_48.predict(X)
    predictions_72 = model_72.predict(X)

    # Create the results df
    d = {'time': X.index.values, 
         'H24': predictions_24.reshape(len(predictions_24)), 
         'H48': predictions_48.reshape(len(predictions_48)), 
         'H72': predictions_72.reshape(len(predictions_72))}

    resultados = pd.DataFrame(d, columns=['time', 'H24', 'H48', 'H72'], index=X.index)
    resultados.to_csv('SALIDA/resultados.csv', index=False)
    
    print('DONE')
    
if __name__ == '__main__':
    print(sys.argv[1])
    main(sys.argv[1])