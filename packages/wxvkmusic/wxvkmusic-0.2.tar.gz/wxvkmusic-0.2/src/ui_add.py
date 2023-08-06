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

from data import get_audios

_ = wx.GetTranslation

class AddDialog(wx.Dialog):
    """ Dialog: Add new playlist by user/community/album's id """    
    
    def __init__(self, *args, **kwargs):
        super(AddDialog, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        """ Load interface """
        
        self.SetTitle(_("Add new..."))
        self.make_layout()
        self.SetInitialSize()
        
        # Events
        self.Bind(wx.EVT_CHECKBOX, self.enable_album, self.album_cb)
        self.add_btn.Bind(wx.EVT_BUTTON, self.get_info, self.add_btn)        
        self.Bind(wx.EVT_CLOSE, self.quit_dial)
        
    def make_layout(self):
        
        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Static texts --- #
        # User/Community/album' id
        id_text = wx.StaticText(self, wx.ID_ANY, _("Id"), 
                                wx.DefaultPosition, wx.DefaultSize, 0)
        id_text.Wrap(-1)
        
        # Playlist's name
        plst_text = wx.StaticText(self, wx.ID_ANY, _("Playlist name"), 
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        plst_text.Wrap(-1)
        
        # --- Text ctrls --- #
        # User/Community id
        self.id_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        
        # Album's id
        self.album_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.album_ctrl.Enable(False)  # disabled by default
        
        # Playlist's name
        self.plst_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        
        # --- RadioBox --- #        
        # ID's type (user, community) box
        rb_choices = [_("User"), _("Community")]
        self.radiobox = wx.RadioBox(self, wx.ID_ANY, wx.EmptyString, 
                                    wx.DefaultPosition, wx.DefaultSize, 
                                    rb_choices, 0, wx.RA_SPECIFY_ROWS)
        
        # --- Checkboxes --- #
        self.album_cb = wx.CheckBox(self, wx.ID_ANY, _("Album"), 
                                    wx.DefaultPosition, wx.DefaultSize, 0)        
        
        # --- Button --- #
        # Add button
        self.add_btn = wx.Button(self, wx.ID_ANY, _("Add"), 
                                 wx.DefaultPosition, wx.DefaultSize, 0)
        
        sizer.AddMany([
            (id_text, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.id_ctrl, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 3),
            (self.radiobox, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5),
            (self.album_cb, 0, wx.ALIGN_CENTER | wx.ALL, 2),
            (self.album_ctrl, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 3),
            (plst_text, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.plst_ctrl, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 3),
            (self.add_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        ])        
        
        self.SetSizer(sizer)
        self.Layout()
        
    def enable_album(self, event):
        """ Enable / disable album text ctrl """
        
        if self.album_cb.GetValue():
            self.album_ctrl.Enable(True)
        else:
            self.album_ctrl.Enable(False)
            
    def get_info(self, event):
        """ Get information about audios """
        
        # Get id
        self.plst_id = self.id_ctrl.GetValue()
        
        if not self.plst_id or self.plst_id == "":
            # If id not entered show error
            wx.MessageBox(_("You need to enter id"), 
                          _("Error"), wx.OK | wx.ICON_ERROR)
            event.Skip()
        else:
            # Check user or community id entered
            sel = self.radiobox.GetSelection()
            if sel == 1:
                # Community ids must start from "-" like "-1"
                if not self.plst_id[0] == "-":
                    self.plst_id = "-" + self.plst_id
            
            # If album checked use it
            if self.album_cb.GetValue():
                self.album = self.album_ctrl.GetValue()
            else:
                self.album = False
            
            # Get audios
            self.audios = get_audios(self.plst_id, self.album)
            
            if not self.audios:
                wx.MessageBox(_("You have not access to audios of entered id"), 
                              _("Error"), wx.OK | wx.ICON_ERROR)
            else:
                self.plst = self.plst_ctrl.GetValue()
                
                # If playlist name not entered, use id as name
                if not self.plst or self.plst == "":
                    self.plst = "ID %s" % self.plst_id
                
                # Close dialog at the end
                self.Destroy()
            
    def quit_dial(self, event):
        """ Close dialog """
        
        self.audios = False
        self.Destroy()
