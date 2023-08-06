import wx
from wx.lib.mixins import listctrl
import sys
from random import random


########################################################################
class ListCtrl(wx.ListCtrl, listctrl.ListCtrlAutoWidthMixin):
    """List class for data table"""

    #----------------------------------------------------------------------
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listctrl.ListCtrlAutoWidthMixin.__init__(self)
        
    
########################################################################
class DataTable(wx.Panel, listctrl.ColumnSorterMixin):
    """Table for view and editing data"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(DataTable, self).__init__(*args, **kwargs)
        #wx.Panel.__init__(self, *args, **kwargs)
        
        self.data = kwargs.get('data')
        self.columns = kwargs.get('columns')
        self.create_and_layout()
        
    
    def create_and_layout(self):
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.list = ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                             |wx.BORDER_NONE
                             |wx.LC_EDIT_LABELS
                             |wx.LC_SORT_ASCENDING)
        
        sizer.Add(self.list, 1, wx.EXPAND)
        
        self.populate_list()
        
        cols_number = len(self.columns)
        self.list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click, self.list)
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.on_right_click)
        #self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.itemDataMap = self.data
        listctrl.ColumnSorterMixin.__init__(self, cols_number)
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        
    def populate_list(self):
        
        if self.columns is None:
            self.columns = ['x', 'y', 'err']
        cols_num = len(self.columns)
        
        for i, col in enumerate(self.columns):
            self.list.InsertColumn(i, col, wx.LIST_FORMAT_RIGHT)
            
        if self.data is None:
            data = dict([(i, [i] + [random()] * cols_num) for i in xrange(10)])
        
        for key, value in data.items():
            index = self.list.InsertStringItem(sys.maxint, str(value[0]))
            for i, v in enumerate(value[1:]):
                self.list.InsertStringItem(index, str(v))
        
        for i in xrange(cols_num):
            self.list.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            
            
        # show how to change the colour of a couple items
        #item = self.list.GetItem(1)
        #item.SetTextColour(wx.BLUE)
        #self.list.SetItem(item)
        #item = self.list.GetItem(4)
        #item.SetTextColour(wx.RED)
        #self.list.SetItem(item)
            
        self.currentItem = 0        

    def GetListCtrl(self):
        return self.list
    
    
    def get_column_text(self, index, col):
        item = self.list.GetItem(index, col)
        return item.GetText()
    
    def on_right_click(self, event):
        index = self.list.GetFirstSelected()
        print index
        
    def on_column_click(self, event):
        print >>sys.stderr, ("OnColClick: %d\n" % event.GetColumn())
        event.Skip()
    
    def on_item_selected(self, event):
        self.currentItem = event.m_itemIndex
        self.data = (self.get_column_text(self.currentItem, 1),
                            self.get_column_text(self.currentItem, 2),
                            self.get_column_text(self.currentItem, 3),
                            self.get_column_text(self.currentItem, 4))( True )    