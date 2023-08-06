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

_ = wx.GetTranslation

class OptionsDialog(wx.Dialog):
    """ Options dialog """
    
    def __init__(self, parent):
        super(OptionsDialog, self).__init__(parent)
        
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        
        self.SetTitle(_("Options"))
        
        self.download_dir = self.parent.download_dir
        self.min_close = self.parent.min_close
        self.sys_gtk_icons = self.parent.sys_gtk_icons
        self.overwrite_files = self.parent.overwrite_files
        self.dlg = None
        
        self.make_layout()
        self.SetInitialSize()
        
        # Events
        self.dir_button.Bind(wx.EVT_BUTTON, self.dir_dialog)
        self.save_button.Bind(wx.EVT_BUTTON, self.get_info)
        self.Bind(wx.EVT_CLOSE, self.quit_dial)
        
    def make_layout(self):
        
        # --- Sizer --- #
        sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Checkboxes --- #
        self.min_close_cb = wx.CheckBox(self, wx.ID_ANY, 
                                        _("Minimize on close"), 
                                        wx.DefaultPosition, wx.DefaultSize, 0)                              
        self.min_close_cb.SetValue(self.min_close)
        
        self.sys_icons_cb = wx.CheckBox(self, wx.ID_ANY, 
                                        _("Use system gtk icons"),
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.sys_icons_cb.SetValue(self.sys_gtk_icons)
        
        self.overwrite_cb = wx.CheckBox(self, wx.ID_ANY, 
                                _("Overwrite existing files when downloading"),
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.overwrite_cb.SetValue(self.overwrite_files)
        
        if not wx.Platform  == "__WXGTK__":
            self.sys_icons_cb.Enable(False)
        
        # --- Buttons --- #
        self.dir_button = wx.Button(self, wx.ID_ANY, 
                                    _("Change download folder"),
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.save_button = wx.Button(self, wx.ID_ANY, _("Save changes"), 
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        
        sizer.AddMany([
            (self.dir_button, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.min_close_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.sys_icons_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.overwrite_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.save_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        ])        
        
        self.SetSizer(sizer)
        self.Layout()
        
    def dir_dialog(self, event):
        """ Create and show download dir choosing dialog """
        
        self.dlg = wx.DirDialog(self, _("Select a folder"), self.download_dir, 
                                wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
                                wx.DefaultPosition, wx.DefaultSize)
        self.dlg.ShowModal()
        
    def get_info(self, event):
        """ Get values from dialog widgets """
        
        self.values = {}
        self.values["min_close"] = self.min_close_cb.GetValue()
        self.values["icons"] = self.sys_icons_cb.GetValue()
        self.values["overwrite"] = self.overwrite_cb.GetValue()
        if self.dlg:
            self.values["ddir"] = self.dlg.GetPath()
        else:
            self.values["ddir"] = self.download_dir
        
        self.Destroy()
        
    def quit_dial(self, event):
        """ Close dialog """
        
        self.values = False
        self.Destroy()
