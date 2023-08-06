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
from data import search_audios

_ = wx.GetTranslation

class SearchDialog(wx.Dialog):
    """ Dialog: Search audiotracks """
    
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        self.init_ui()
    
    def init_ui(self):
        """ Load interface """
        
        self.SetTitle(_("Search"))
        self.make_layout()               
        self.SetInitialSize()
        
        # Events
        self.btn.Bind(wx.EVT_BUTTON, self.get_info, self.btn)
        self.Bind(wx.EVT_CLOSE, self.quit_dial)
        
    def make_layout(self):
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Static text --- #
        st_text = wx.StaticText(self, wx.ID_ANY, _("Search"), 
                                wx.DefaultPosition, wx.DefaultSize, 0)
        st_text.Wrap(-1)
        
        # --- Text ctrl --- #
        self.ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                wx.DefaultPosition, wx.DefaultSize, 0)
                                
        # --- Checkboxes --- #
        # Search only by artist
        self.perfomer_only_cb = wx.CheckBox(self, wx.ID_ANY, 
                                            _("Search by artist only"), 
                                            wx.DefaultPosition, wx.DefaultSize, 
                                            0)
        # Search only in my audios                                    
        self.my_audios_cb = wx.CheckBox(self, wx.ID_ANY, 
                                        _("Search in my audios"),
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        # If query have mistakes they can be fixed automatically
        self.fix_query_cb = wx.CheckBox(self, wx.ID_ANY, 
                                        _("Fix possible mistakes in query"),
                                        wx.DefaultPosition, wx.DefaultSize, 0)
                                
        # --- Button --- #
        self.btn = wx.Button(self, wx.ID_ANY, _("Search"), 
                             wx.DefaultPosition, wx.DefaultSize, 0)
                             
        sizer.AddMany([
            (st_text, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.ctrl, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 3),
            (self.perfomer_only_cb, 0, wx.ALIGN_CENTER | wx.ALL, 2),
            (self.my_audios_cb, 0, wx.ALIGN_CENTER | wx.ALL, 2),
            (self.fix_query_cb, 0, wx.ALIGN_CENTER | wx.ALL, 2),
            (self.btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        ])
        
        self.SetSizer(sizer)
        self.Layout()
        
    def get_info(self, event):
        """ Get information about audios """
        
        # Get query
        self.query = self.ctrl.GetValue()
        
        if not self.query or self.query == "":
            # If query not entered show error
            wx.MessageBox(_("You need to enter query"), 
                          _("Error"), wx.OK | wx.ICON_ERROR)
            event.Skip()
        else:
            
            perfomer_only = int(self.perfomer_only_cb.GetValue())
            my_audios = int(self.my_audios_cb.GetValue())
            fix_query = int(self.fix_query_cb.GetValue())
            
            # Get audios
            self.audios = search_audios(self.query, perfomer_only, my_audios,
                                        fix_query)
            
            # If audios were not got or 0 (zero) audios got show error
            if type(self.audios) == dict:
                if self.audios["count"] == 0:
                    self.audios = False
            
            if not self.audios:
                wx.MessageBox(_("No audios found"), 
                              _("Error"), wx.OK | wx.ICON_ERROR)
            else:
                # Close dialog at the end
                self.Destroy()
    
    def quit_dial(self, event):
        """ Close dialog """
        
        self.audios = False
        self.Destroy()
