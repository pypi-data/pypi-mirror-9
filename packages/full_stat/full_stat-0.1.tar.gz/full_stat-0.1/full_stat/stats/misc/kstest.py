__author__ = 'yarnaid'

import numpy as np
from scipy.stats import ks_2samp


def kstest(df, x_col=None, y_col=None, *args, **kwargs):
    if len(df) < 1:
        return 0
    if x_col is not None:
        x = df[x_col].values
    else:
        x = df.x
    if y_col is not None:
        y = df[y_col]
    else:
        y = df.y
    try:
        return float(ks_2samp(x, y)[0])
    except Exception as e:
        print ks_2samp(x, y)
        raise e