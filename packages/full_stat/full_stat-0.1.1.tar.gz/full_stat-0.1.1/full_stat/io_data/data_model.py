__author__ = 'yarnaid'


from pandas import DataFrame
from PySide import QtCore


class Data(QtCore.QObject):
    """
    Wrapper for pandas DataFrame. It's created to add signals
    for GUI processing.
    """
    updated = QtCore.Signal(DataFrame)
    loaded = QtCore.Signal(DataFrame)

    df = DataFrame()

    def __init__(self, *args, **kwrags):
        super(Data, self).__init__(*args, **kwrags)
