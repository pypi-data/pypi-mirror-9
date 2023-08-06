__author__ = 'yarnaid'

import sys
import os
import platform
from PySide import QtGui, QtCore
from PySide.QtGui import QMainWindow, QMessageBox
import pandas as pd

import PySide
import pyqtgraph as pg

import full_stat

__version__ = '0.1'


class MainWindow(QMainWindow):
    """
    Mai GUI class
    """

    def init_layout(self):
        self.cw = QtGui.QWidget()
        self.layout = QtGui.QHBoxLayout()
        self.left_layout = QtGui.QVBoxLayout()
        self.right_layout = QtGui.QVBoxLayout()
        self.cw.setLayout(self.layout)
        self.setCentralWidget(self.cw)

    def fill_layout(self):
        self.left_layout.addWidget(self.mean_group_box)
        self.left_layout.addWidget(self.corr_group_box)
        self.left_layout.addWidget(self.misc_group_box)

        self.right_layout.addWidget(self.tabs)
        self.layout.addLayout(self.left_layout)
        self.layout.stretch(1)
        self.layout.addLayout(self.right_layout)
        self.setLayout(self.layout)

    def init_ui(self, title):
        self.init_menus()
        self.init_toolbar()
        self.init_tabs()
        self.init_stat_view()
        self.setWindowTitle(title)
        # self.resize(300, 200)

        self.init_layout()

        self.statusBar().showMessage('Ready')

        self.fill_layout()

    def init_stat_view(self):
        # start
        self.stat_units = list()

        # Mean Values
        self.mean_group_box = QtGui.QGroupBox(self.tr('Mean Values'))
        mean_layout = QtGui.QFormLayout()

        self.mean_line_edits = dict()

        ViewWidget = QtGui.QLineEdit

        def add_stat(name, calc, **cols):
            mean_widget = ViewWidget()
            mean_widget.setDisabled(True)
            stat_unit = StatUnit(name, calc, mean_widget, **cols)
            self.df.updated.connect(stat_unit.update_widget)
            stat_unit.add_to_form_layout(mean_layout)
            self.stat_units.append(stat_unit)  # to keep pointer in memory and not to destroy it

        add_stat('Arithmetic', full_stat.stats.mean.arithm, y_col='y')  # TODO: fix translation
        add_stat('Median', full_stat.stats.mean.median, y_col='y')  # TODO: fix translation
        add_stat('Weighted (by errors)', full_stat.stats.mean.weighted, y_col='y', err_col='y_err')  # TODO: fix translation

        # Correlations
        self.corr_group_box = QtGui.QGroupBox(self.tr('Correlation'))
        corr_layout = QtGui.QFormLayout()
        corr_layout.addWidget(QtGui.QLabel('<i>Over first 2 columns</i>'))

        def add_corr(name, calc):
            corr_widget = ViewWidget()
            corr_widget.setDisabled(True)
            stat_unit = StatUnit(name, calc, corr_widget)
            self.df.updated.connect(stat_unit.update_widget)
            stat_unit.add_to_form_layout(corr_layout)
            self.stat_units.append(stat_unit)

        add_corr('Pearson', full_stat.stats.corr.pearson)
        add_corr('Kendall', full_stat.stats.corr.kendall)

        # Other statistics
        self.misc_group_box = QtGui.QGroupBox(self.tr('Other'))
        misc_layout = QtGui.QFormLayout()
        misc_layout.addWidget(QtGui.QLabel('<i>Over first 2 columns</i>'))

        def add_other(name, calc):
            widget = ViewWidget()
            widget.setDisabled(True)
            stat_unit = StatUnit(name, calc, widget)
            self.df.updated.connect(stat_unit.update_widget)
            stat_unit.add_to_form_layout(misc_layout)
            self.stat_units.append(stat_unit)

        add_other('Kruskal-Wallis', full_stat.stats.misc.kwallis)
        add_other('Kolmogorov-Smirnov', full_stat.stats.misc.kstest)

        self.mean_group_box.setLayout(mean_layout)
        self.corr_group_box.setLayout(corr_layout)
        self.misc_group_box.setLayout(misc_layout)

    def init_connections(self):
        self.df.loaded.connect(self.on_data_loaded)
        self.df.updated.connect(self.data_tab.update_table)
        self.df.updated.connect(self.plot_tab.update_plot)

    def __init__(self, parent=None, title=''):
        super(MainWindow, self).__init__(parent)
        self.settings = QtCore.QSettings()
        self.read_settings()
        self.df = full_stat.Data()
        self.init_ui(title)

        self.last_load_path = self.settings.value('paths/last', './')
        self.init_connections()

    def buttonTest(self):
        print 'Test OK'

    def init_actions(self):
        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        self.exit_action = exit_action

        load_action = QtGui.QAction('&Load', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setStatusTip('Load data')
        load_action.triggered.connect(self.load_data)
        self.load_action = load_action

        about_action = QtGui.QAction('&About', self)
        about_action.setStatusTip('About application')
        about_action.triggered.connect(self.about)
        self.about_action = about_action

    def init_menus(self):
        self.init_actions()

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.exit_action)
        file_menu.addAction(self.about_action)

    def init_toolbar(self):
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.load_action)
        self.toolbar.addAction(self.exit_action)
        self.toolbar.addAction(self.about_action)

    def on_data_loaded(self, df):
        self.df.updated.emit(df)

    def load_data(self):
        file_name, __ = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open file'), self.settings.value('path/last'))
        last_path = os.path.abspath(file_name)
        last_dir = os.path.dirname(last_path)
        self.settings.setValue('path/last', last_dir)

        self.df.df = full_stat.read_csv(file_name)
        self.df.loaded.emit(self.df.df)

    def about(self):
        """Popup a box with about message."""
        QMessageBox.about(self, "About {} Application".format(self.settings.applicationName()),
                          """<b> About this program </b> v %s
               <p>Copyright 2015 Yaroslav Nayden.
               All rights reserved in accordance with
               GPL v3 or later - NO WARRANTIES!
               <p>This application can be used for
               getting statistics over arrays of data.
               <p>Python %s -  PySide version %s - Qt version %s on %s""" % \
                          (__version__, platform.python_version(), PySide.__version__, \
                           PySide.QtCore.__version__, platform.system()))

    def init_tabs(self):
        self.tabs = QtGui.QTabWidget()
        self.data_tab = Table()
        self.tabs.addTab(self.data_tab, self.tr('Data'))
        self.plot_tab = Plot()
        self.tabs.addTab(self.plot_tab, self.tr('Plot'))

    def save_settings(self):
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.endGroup()

    def read_settings(self):
        self.settings.beginGroup("MainWindow")
        self.resize(self.settings.value("size", QtCore.QSize(400, 400)))
        self.move(self.settings.value("pos", QtCore.QPoint(400, 800)))
        self.settings.endGroup()

    def closeEvent(self, event):
        self.save_settings()
        # if self.userReallyWantsToQuit():
        #     self.save_settings()
        #     event.accept()
        # else:
        #     event.ignore()


class StatUnit(QtCore.QObject):

    def __init__(self, name, evaluate, widget, x_col=None, y_col=None, err_col=None, *args, **kwargs):
        super(StatUnit, self).__init__(*args, **kwargs)
        self.name = name
        self.evaluate = evaluate
        self.widget = widget
        self.x_col = x_col
        self.y_col = y_col
        self.err_col = err_col

    def update_widget(self, df):
        value = self.evaluate(df, x_col=self.x_col, y_col=self.y_col, err_col=self.err_col)
        self.widget.setText('{:1.3f}'.format(value))

    def add_to_form_layout(self, layout):
        layout.addRow(self.tr(self.name) + ':', self.widget)


class Table(QtGui.QWidget):
    ''' table tab-widget for main app
    '''

    def __init__(self, parent=None):
        super(Table, self).__init__(parent)

        cols = 3
        rows = 0
        self.table = QtGui.QTableWidget(rows, cols, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.table)

        self.setLayout(layout)

    # @QtCore.Slot(pd.DataFrame)
    def update_table(self, df):
        self.table.clearContents()
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns.values)
        for i, row in enumerate(df.iterrows()):
            for j, col in enumerate(row[1]):
                cell = QtGui.QTableWidgetItem('{:2.3f}'.format(float(col)))
                self.table.setItem(i, j, cell)


class Plot(QtGui.QWidget):
    """
    Widget for plot
    """

    def __init__(self, parent=None):
        super(Plot, self).__init__(parent)
        layout = QtGui.QVBoxLayout()

        self.plot_widget = pg.PlotWidget(name='Data')
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)
        self.update_plot(pd.DataFrame())

    def update_plot(self, df):
        self.plot_widget.plot(df.get('x', [0]), df.get('y', [0]))