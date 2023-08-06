__author__ = 'yarnaid'

import wx
from gui.app import FullStatFrame
from gui_pyside import app as app_qt

TITLE = 'Full Stat'


def run_gui():
    app = wx.App()
    frame = FullStatFrame(None, title=TITLE)
    app.MainLoop()


def run_qt():
    app_qt.main()

def main():
    run_qt()

if __name__ == '__main__':
    main()