__author__ = 'yarnaid'

import numpy as np
import pandas as pd


def mean(arr, y_col=None, *args, **kwargs):
    if len(arr) < 1:
        return 0
    if y_col is not None:
        arr = arr[y_col].values
    if isinstance(arr, list):
        arr = np.asarray(arr)
    return float(pd.DataFrame(arr).median())