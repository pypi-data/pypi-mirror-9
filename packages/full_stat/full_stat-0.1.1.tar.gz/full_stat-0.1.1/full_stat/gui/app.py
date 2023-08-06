import wx
import wx.grid as gridlib
import os

from data_table import DataTable

APP_EXIT = 1
_ = wx.GetTranslation


class FullStatFrame(wx.Frame):
    '''Main frame class for application'''
    
    def __init__(self, *args, **kwargs):
        super(FullStatFrame, self).__init__(*args, **kwargs)
        
        self.init_ui()
        
        
    def init_ui(self):
        
        self.panel = wx.Panel(self)
        
        self.init_menus()
        
        self.init_panels()
        
        
        self.Show()
        self.Center()
        
        
    def init_panels(self):
        main_box = wx.BoxSizer(wx.HORIZONTAL)
        
        self.panel.SetBackgroundColour('#4f5049')
        
        left_panel = wx.Panel(self.panel)
        left_panel.SetBackgroundColour('#ededed')
        b1 = wx.Button(left_panel, -1, label='b1')
        
        right_panel = wx.Panel(self.panel)
        right_panel.SetBackgroundColour('#000000')
        b2 = wx.Button(right_panel, -1, label='b2')
        
        main_box.Add(left_panel, 1, wx.EXPAND|wx.ALL, 20)
        main_box.Add(right_panel, 1, wx.EXPAND|wx.ALL, 20)
        
        self.panel.SetSizer(main_box)

    def init_menus(self):
        menubar = wx.MenuBar()
        
        view_menu = wx.Menu()
        
        self.view_menu_toogle_status_bar = view_menu.Append(wx.ID_ANY,
                                                            '{}\tCtrl+Shift+S'.format(_('Toogle Status Bar')),
                                                       kind=wx.ITEM_CHECK)
        view_menu.Check(self.view_menu_toogle_status_bar.GetId(), True)
        self.Bind(wx.EVT_MENU, self.on_toggle_status_bar, self.view_menu_toogle_status_bar)
        
        file_menu = wx.Menu()
        
        file_menu_open = file_menu.Append(wx.ID_OPEN, '&{}\tCtrl+O'.format(_('Open')))
        self.Bind(wx.EVT_MENU, self.on_open, file_menu_open)
        
        file_menu_save = file_menu.Append(wx.ID_SAVE, '&{}\tCtrl+S'.format(_('Save')))
        self.Bind(wx.EVT_MENU, self.on_save, file_menu_save)

        file_menu.AppendSeparator()
        
        file_menu_quit = wx.MenuItem(file_menu, APP_EXIT, '&{}\tCtrl+Q'.format(_('Quit')))
        if os.path.exists('exti.png'):
            file_menu_quit.SetBitmap(wx.Bitmap('exit.png'))
        file_menu.AppendItem(file_menu_quit)
        self.Bind(wx.EVT_MENU, self.on_quit, file_menu_quit)
        
        #about_menu_item = wx.MenuItem(None, id=wx.ID_ABOUT, text='About')
        
        menubar.Append(file_menu, '&{}'.format(_('File')))
        menubar.Append(view_menu, '&{}'.format(_('View')))
        #menubar.Append(about_menu_item, 'About')
        
        self.SetMenuBar(menubar)
        
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText(_('Ready'))
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        
    def on_save(self, e):
        raise NotImplementedError
        
        
    def on_right_down(self, e):
        self.PopupMenu(ContextMenu(self), e.GetPosition())
        
        
    def on_quit(self, e):
        self.Close()
        
    
    def on_open(self, e):
        raise NotImplementedError
    
    def on_toggle_status_bar(self, e):
        if self.view_menu_toogle_status_bar.IsChecked():
            self.status_bar.Show()
        else:
            self.status_bar.Hide()


########################################################################
class ContextMenu(wx.Menu):
    """Context menu of application"""

    #----------------------------------------------------------------------
    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        
        super(ContextMenu, self).__init__(*args, **kwargs)
    
        self.parent = parent
        
        minimize_item = wx.MenuItem(self, wx.NewId(), 'Minimize')
        self.AppendItem(minimize_item)
        self.Bind(wx.EVT_MENU, self.on_minimize, minimize_item)
    
    
    def on_minimize(self, e):
        self.parent.Iconize()    