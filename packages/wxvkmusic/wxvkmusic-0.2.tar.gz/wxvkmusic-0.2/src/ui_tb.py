#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
# wx VK Music 
# Free & OpenSource music player for vk.com social network
# https://bitbucket.org/xxblx/wx-vk-music
# 
# Oleg Kozlov (xxblx), 2014 - 2015
###########################################################

import wx

from conf import get_icon_path

_ = wx.GetTranslation

class TaskbarIcon(wx.TaskBarIcon):
    """ Taskbar Icon """
    
    def __init__(self, *args, **kwargs):
        super(TaskbarIcon, self).__init__(*args, **kwargs)
        
        self.icon = wx.Icon(get_icon_path("icon.png"), wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icon, "wx VK Music")
        
        self.make_menu()       
        
    def make_menu(self):
        """ Make a popup menu """        
        
        # Events IDs
        self.ID_TB_NEXT = wx.NewId()
        self.ID_TB_PREV = wx.NewId()
        self.ID_TB_PAUSE = wx.NewId()
        self.ID_TB_STOP = wx.NewId()
        self.ID_TB_SHOW = wx.NewId()
        self.ID_TB_RANDOM_TRACK = wx.NewId()
        
        # Menu
        self.menu = wx.Menu()
        self.menu.Append(self.ID_TB_SHOW, _("&Show/Hide app window"), 
                         wx.EmptyString)
        self.menu.Append(self.ID_TB_PAUSE, _("&Play/Pause"), wx.EmptyString)
        self.menu.Append(self.ID_TB_PREV, _("&Previous"), wx.EmptyString)
        self.menu.Append(self.ID_TB_NEXT, _("&Next"), wx.EmptyString)
        self.menu.Append(self.ID_TB_RANDOM_TRACK, 
                         _("&Random audiotrack"), wx.EmptyString)
        self.menu.Append(self.ID_TB_STOP, _("&Stop"), wx.EmptyString)
        self.menu.Append(wx.ID_EXIT, _("&Quit"), wx.EmptyString)
        
        # Show menu by right click
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.show_menu)
        
    def show_menu(self, event):
        """ Show menu """
        
        self.PopupMenu(self.menu)
