__author__ = 'yarnaid'

import pandas as pd
import numpy as np
from data_model import Data


def read_csv(file_name):
    '''
    :param file_name: file with input data
    :return: pandas.DataFrame with data

    TODO: Add feature to select column names

    '''

    names = ['x', 'y', 'y_err']
    df = pd.read_csv(file_name, names=names, dtype=pd.np.float64)
    if len(df[names[-1]]) < 1:
        df[names[-1]] = pd.Series(np.zeros(len(df)))
    df.dropna()
    # columns = df.columns.values

    return df