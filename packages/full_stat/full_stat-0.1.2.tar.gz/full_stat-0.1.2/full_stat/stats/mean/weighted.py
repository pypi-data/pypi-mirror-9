__author__ = 'yarnaid'

import numpy as np


def corr(df, y_col=None, err_col=None, *args, **kwargs):
    if len(df) < 1:
        return 0
    if y_col is not None:
        y = df[y_col].values
    else:
        y = df.y
    if err_col is not None:
        err = df[err_col]
    else:
        err = df.y_err
    return float(np.average(y, None, err))