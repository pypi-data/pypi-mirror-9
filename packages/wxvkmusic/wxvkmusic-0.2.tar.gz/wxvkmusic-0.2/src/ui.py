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
import wx.aui
import wx.media
import wx.lib.mixins.listctrl as mixlc

from ui_add import AddDialog
from ui_options import OptionsDialog
from ui_tb import TaskbarIcon
from ui_search import SearchDialog
from ui_downloader import DownloaderDialog

import data
import conf

_ = wx.GetTranslation

class MainFrame(wx.Frame):
    """ Main app frame """
    
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)

        self.init_ui()
        
    def init_ui(self):
        """ Load interface """      
        
        self.SetSize((600, 400))  # size    
        self.SetTitle("wx VK Music")  # frame's title
        self.Centre()  # move to center of screen
        
        # Locale
        self.update_locale()
        
        # This dict will contain info about playlists and audiotracks
        self.audios = {}
        
        # This list will have 4 values: page; index and N of currenly 
        # playing audiotrack and name of playlist's section
        self.now_playing = [0, 0, 0, None]
        
        self.play = False  # any audiotrack playing now
        self.pause = False  # playing paused
        self.muted = False  # volume muted
        self.repeat = False  # repeat current audiotrack
        self.reverse = False  # playlist playing in reverse order
        self.random = False  # playlist playing in random order
        
        self.search_results = {}  # opened tabs with search results
        
        self.downloader = None  # audiotracks downloader
        # Overwrite exist files when downloading
        self.overwrite_files = True
        
        # MediaCtrl
        # It has ShowPlayerControls method, but it does not support 
        # GStreamer, that mean it is not available on GNU/Linux. It is 
        # the reason why mediaCtrl will be hide.
        # Instead of his controls (step, vol) will be created two sliders.
        self.media = wx.media.MediaCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                        wx.DefaultPosition, wx.DefaultSize)
        self.media.SetPlaybackRate(1)
        self.media.Hide()

        # Timer
        self.timer = wx.Timer(self)
        
        self.make_menubar()
        self.make_statusbar()
        self.make_taskbar()
        self.make_layout()
        
        self.sign_in()  # login
        self.load_playlists()  # add pages with playlists from config
        self.load_params()  # load app parametres
        self.update_bitmaps()
        
        self.Show(True)  # show frame
                               
        # --- Events --- #
        if self.min_close:
            # Hide app windows if close button pressed
            self.Bind(wx.EVT_CLOSE, self.show_hide_app)
        else:
            # Close all windows and taskbar icon if main frame closed
            self.Bind(wx.EVT_CLOSE, self.quit_app)
        
        # Key pressing !!!NOT GLOBAL!!! This bind work for this frame only
        self.Bind(wx.EVT_CHAR_HOOK, self.key_pressing)
        
        # Volume regulation
        self.Bind(wx.EVT_SLIDER, self.set_volume, self.volume_sl)
        
        # Scrolling audiotrack
        self.Bind(wx.EVT_SLIDER, self.scroll_progress, self.progress_sl)
        
        # Mute / Unmute button
        self.volume_btn.Bind(wx.EVT_BUTTON, self.mute_volume)
        
        # Prev / Next audiotrack buttons
        self.prev_btn.Bind(wx.EVT_BUTTON, self.play_prev)
        self.next_btn.Bind(wx.EVT_BUTTON, self.play_next)
        
        # Stop button
        self.stop_btn.Bind(wx.EVT_BUTTON, self.stop_playing)
        
        # Play / pause button 
        self.play_btn.Bind(wx.EVT_BUTTON, self.play_pause)
        
        # Audiotrack playing progress
        self.Bind(wx.EVT_TIMER, self.upd_progress_slider)
        
        # Audiotrack playing finish
        # If reverse playing on, play prev track if current finished
        if self.reverse:
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_prev)
        # If random playing, play random track if current finished
        elif self.random:
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_random)
        else:
            # Play next track if current finished
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_next)
        
        # Remove playlist if page closed
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.rm_plst)
    
    def update_locale(self):
        """ Update list of available locales """        
        
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT) 
        self.locale.AddCatalogLookupPathPrefix(conf.get_locale_path())
        self.locale.AddCatalog("wxvkmusic")
    
    def make_menubar(self):
        """ Main frame menubar, menus and items """
        
        ID_REPEAT = wx.NewId()
        ID_REVERSE = wx.NewId()
        ID_RANDOM = wx.NewId()
        ID_RANDOM_TRACK = wx.NewId()
        ID_SHOW_DOWNLOADER = wx.NewId()
        ID_DOWNLOAD_SELECTED = wx.NewId()
        ID_DOWNLOAD_PLAYING = wx.NewId()
        ID_DOWNLOAD_PLAYLIST = wx.NewId()
        
        menubar = wx.MenuBar()
        
        # Menus
        file_menu = wx.Menu()
        help_menu = wx.Menu()
        play_menu = wx.Menu()
        download_menu = wx.Menu()
        
        # File menu
        file_menu.Append(wx.ID_ADD, _("&Add\tCtrl+N"), _("Add new playlist"))
        file_menu.Append(wx.ID_FIND, _("&Search\tCtrl+F"), 
                         _("Search audiotracks"))
        file_menu.Append(wx.ID_PROPERTIES, _("&Options\tCtrl+O"), 
                         _("Open options dialog"))
        file_menu.Append(wx.ID_EXIT, _("&Quit\tCtrl+Q"), _("Quit app"))
        
        # Play menu - Reverse item
        self.play_menu_reverse = wx.MenuItem(None, ID_REVERSE, 
                                             _("&Reverse\tCtrl+P"),
                                            _("Reverse playlist playing"), 
                                            wx.ITEM_CHECK)
        # Play menu - Random item
        self.play_menu_random = wx.MenuItem(None, ID_RANDOM, 
                                            _("&Random playing\tShift+R"),
                                        _("Play audiotracks in random order"), 
                                            wx.ITEM_CHECK)
        
        # Play menu                                   
        play_menu.Append(ID_REPEAT, _("&Repeat\tCtrl+R"), 
                         _("Repeat current audiotrack"), wx.ITEM_CHECK)
        play_menu.AppendItem(self.play_menu_reverse)  # reverse playing
        play_menu.Append(ID_RANDOM_TRACK, 
                         _("&Random audiotrack\tCtrl+Shift+R"),
                         _("Play one random audiotrack"))
        play_menu.AppendItem(self.play_menu_random)  # random playing
        
        # Download menu 
        download_menu.Append(ID_DOWNLOAD_SELECTED, 
                             _("&Download selected\tCtrl+D"), 
                             _("Download selected audiotrack"))
        download_menu.Append(ID_DOWNLOAD_PLAYING, 
                             _("&Download playing\tShift+D"),
                             _("Download playing audiotrack"))
        download_menu.Append(ID_DOWNLOAD_PLAYLIST, _("&Download playlist"),
                             _("Download all audiotracks from this playlist"))
        download_menu.AppendSeparator()
        download_menu.Append(ID_SHOW_DOWNLOADER, 
                             _("&Show downloader\tCtrl+Shift+D"), 
                             _("Open downloader dialog"))
        
        # Help menu
        help_menu.Append(wx.ID_ABOUT, _("&About"), _("About application"))
        
        # Menu events
        self.Bind(wx.EVT_MENU, self.add_plst, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.open_search, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.open_app_opts, id=wx.ID_PROPERTIES)
        self.Bind(wx.EVT_MENU, self.quit_app, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.show_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.switch_repeat, id=ID_REPEAT)
        self.Bind(wx.EVT_MENU, self.switch_reverse, id=ID_REVERSE)
        self.Bind(wx.EVT_MENU, self.play_random, id=ID_RANDOM_TRACK)
        self.Bind(wx.EVT_MENU, self.switch_random, id=ID_RANDOM)
        self.Bind(wx.EVT_MENU, self.show_downloader, id=ID_SHOW_DOWNLOADER)
        self.Bind(wx.EVT_MENU, self.download_selected, id=ID_DOWNLOAD_SELECTED)
        self.Bind(wx.EVT_MENU, self.download_playing, id=ID_DOWNLOAD_PLAYING)
        self.Bind(wx.EVT_MENU, self.download_playlist, id=ID_DOWNLOAD_PLAYLIST)
        
        menubar.Append(file_menu, _("&File"))
        menubar.Append(play_menu, _("&Play"))
        menubar.Append(download_menu, _("&Download"))
        menubar.Append(help_menu, _("&Help"))
        
        self.SetMenuBar(menubar)
        
    def make_statusbar(self):
        self.statusbar = self.CreateStatusBar()
    
    def make_taskbar(self):
        
        # Make a TaskbarIcon
        self.taskbar = TaskbarIcon()
        
        # TaskBarIcon events
        self.taskbar.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.show_hide_app)
        self.taskbar.Bind(wx.EVT_MENU, self.show_hide_app, 
                          id=self.taskbar.ID_TB_SHOW)
        self.taskbar.Bind(wx.EVT_MENU, self.play_pause, 
                          id=self.taskbar.ID_TB_PAUSE)
        self.taskbar.Bind(wx.EVT_MENU, self.play_prev, 
                          id=self.taskbar.ID_TB_PREV)
        self.taskbar.Bind(wx.EVT_MENU, self.play_next, 
                          id=self.taskbar.ID_TB_NEXT)
        self.taskbar.Bind(wx.EVT_MENU, self.stop_playing, 
                          id=self.taskbar.ID_TB_STOP)
        self.taskbar.Bind(wx.EVT_MENU, self.play_random, 
                          id=self.taskbar.ID_TB_RANDOM_TRACK)
        self.taskbar.Bind(wx.EVT_MENU, self.quit_app, id=wx.ID_EXIT)
        
    def make_layout(self):
        """ Add widgets to frame """
        
        # Sizers
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        audio_sizer = wx.BoxSizer(wx.HORIZONTAL)  # sizer for audio controls
                
        # --- Bitmap buttons --- #
        # Media buttons: stop, play/pause, prev, next, (un)mute 
        self.stop_btn = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, 
                                        style=wx.NO_BORDER)
        self.play_btn = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, 
                                        style=wx.NO_BORDER)
        self.prev_btn = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, 
                                        style=wx.NO_BORDER)
        self.next_btn = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, 
                                        style=wx.NO_BORDER)
        self.volume_btn = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, 
                                          style=wx.NO_BORDER)
        
        # --- Sliders --- #
        # Audio track's progress line (slider)
        self.progress_sl = wx.Slider(self, wx.ID_ANY, 0, 0, 0, 
                                     style=wx.SL_HORIZONTAL)
        
        # Volume slider
        self.volume_sl = wx.Slider(self, wx.ID_ANY, 0, 0, 100, 
                                   style=wx.SL_HORIZONTAL)      
        
        # --- Notebook --- #
        # Notebook with playlists
        self.notebook = wx.aui.AuiNotebook(self, wx.ID_ANY, 
                                           style=wx.aui.AUI_NB_DEFAULT_STYLE)

        # --- Add widgets to sizers --- #
        # Audio sizer
        audio_sizer.AddMany([
            (self.stop_btn, 0, wx.ALL, 3),  # stop
            (self.play_btn, 0, wx.ALL, 3),  # play
            (self.prev_btn, 0, wx.ALL, 3),  # previous track
            (self.next_btn, 0, wx.ALL, 3),  # next track
            (self.progress_sl, 3, wx.ALL | wx.EXPAND, 3), # progress line
            (self.volume_btn, 0, wx.ALL, 3),  # mute volume
            (self.volume_sl, 1, wx.ALL | wx.EXPAND, 3)  # volume slider
        ])        
        
        # Main sizer
        main_sizer.Add(audio_sizer, 0, wx.ALL | wx.EXPAND, 5)  # audio sizer
        main_sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)  # notebook
        
        self.SetSizer(main_sizer)
        self.Layout()
    
    def init_bundled_bitmaps(self):
        """ Use icons bundled with app """
        
        self.stop_bitmap = wx.Bitmap(conf.get_icon_path("stop.png"))
        self.play_bitmap = wx.Bitmap(conf.get_icon_path("play.png"))
        self.pause_bitmap = wx.Bitmap(conf.get_icon_path("pause.png"))
        self.prev_bitmap = wx.Bitmap(conf.get_icon_path("prev.png"))
        self.next_bitmap = wx.Bitmap(conf.get_icon_path("next.png"))
        self.vol_on_bitmap = wx.Bitmap(conf.get_icon_path("volume.png"))
        self.vol_off_bitmap = wx.Bitmap(conf.get_icon_path("volume_mute.png"))
    
    def init_sys_gtk_bitmaps(self):
        """ Use icons from system gtk theme """
        
        # Stop
        self.stop_bitmap = wx.ArtProvider.GetBitmap("gtk-media-stop", 
                                                    size=(24, 24))
        
        # Play / pause
        self.play_bitmap = wx.ArtProvider.GetBitmap("gtk-media-play", 
                                                    size=(24, 24))
        self.pause_bitmap = wx.ArtProvider.GetBitmap("gtk-media-pause", 
                                                    size=(24, 24))

        # Next / Prev
        self.prev_bitmap = wx.ArtProvider.GetBitmap("gtk-media-previous", 
                                                    size=(24, 24))
        self.next_bitmap = wx.ArtProvider.GetBitmap("gtk-media-next", 
                                                    size=(24, 24))
                
        # Volume on /off        
        self.vol_on_bitmap = wx.ArtProvider.GetBitmap("audio-volume-high", 
                                                      size=(24, 24))
        self.vol_off_bitmap = wx.ArtProvider.GetBitmap("audio-volume-muted", 
                                                       size=(24, 24))
        
    def update_bitmaps(self):
        """ 
        Switching between system gtk icons (bitmaps) and bundled 
        with app icons (bitmaps - play.png, stop.png, etc.) 
        """
        
        if self.sys_gtk_icons and wx.Platform == "__WXGTK__":
            self.init_sys_gtk_bitmaps()
        else:
            self.init_bundled_bitmaps()
        
        # --- Set new icons to buttons --- #
        # Stop button
        self.stop_btn.SetBitmapLabel(self.stop_bitmap)
        
        # Play / Pause buttons
        if (not self.play) or self.pause:
            self.play_btn.SetBitmapLabel(self.play_bitmap)
        else:
            self.play_btn.SetBitmapLabel(self.pause_bitmap)
        
        # Prev / Next buttons
        self.prev_btn.SetBitmapLabel(self.prev_bitmap)
        self.next_btn.SetBitmapLabel(self.next_bitmap)   
        
        # Volume button
        if not self.muted and not self.play:
            self.volume_btn.SetBitmapLabel(self.vol_on_bitmap)
        elif not self.muted and self.play:
            if self.media.GetVolume() > 0:
                self.volume_btn.SetBitmapLabel(self.vol_on_bitmap) 
            else:
                self.volume_btn.SetBitmapLabel(self.vol_off_bitmap)
        else:
            self.volume_btn.SetBitmapLabel(self.vol_off_bitmap)
    
    def switch_onclose_bind(self):
        """ Swith bind for window closing """
        
        # Unbind current action        
        self.Unbind(wx.EVT_CLOSE)
        
        # Bind new action for EVT_CLOSE event
        if not self.min_close:
            self.Bind(wx.EVT_CLOSE, self.quit_app)
        else:
            self.Bind(wx.EVT_CLOSE, self.show_hide_app)         
    
    def show_hide_app(self, event):
        """ Show/Hide app's window """
        
        if self.IsShown():        
            self.Show(False)
        else:
            self.Show(True)
    
    def quit_app(self, event):
        """ Quit application """
        
        # Save active tab num and volume level to config
        conf.save_params(self.volume_sl.GetValue(),  # vol
                         self.notebook.GetSelection(),  # tab
                         self.min_close,  # minimize on close
                         self.sys_gtk_icons,  # use ot not system gtk icons
                         self.reverse,  #  play prev track after current
                         self.random,  # play random track after current
                         self.download_dir,  # download directory
                         self.overwrite_files)  # overwrite files
        
        conf.save_conf()  # save config's changes
        self.Destroy()
        self.taskbar.Destroy()
        if self.downloader:
            self.downloader.Destroy()
    
    def show_about(self, event):
        """ Show about dialog with app info """
        
        desc = """wx VK Music is Free & OpenSource crossplatform 
music player for vk.com social network."""

        artists = (
            "TaskBar Icon by Ivlichev Victor Petrovich",
            "http://iconfindr.com/1zAqSb3 (CC BY 3.0)",
            " ",
            "Media control buttons - from Faenza icons set",
            "http://fav.me/d2v6x24 (GNU GPL v3)"
        )
        
        developers = (
            "Author & Developer",
            "Oleg Kozlov (xxblx) <xxblx.oleg@yandex.com>",
            "",
            "Some fixes and improvements",
            "Timur Enikeev <te1da@yandex.ru>"
        )
        
        translators = (
            "ru - Oleg Kozlov",
            ""
        )
                
        info = wx.AboutDialogInfo()
        info.SetName("wx VK Music")
        info.SetDescription(desc)
        info.SetVersion("0.2")
        info.SetCopyright("(C) 2014-2015 Oleg Kozlov (xxblx)")
        info.SetArtists(artists)
        info.SetTranslators(translators)
        info.SetDevelopers(developers)
        info.SetWebSite("https://bitbucket.org/xxblx/wx-vk-music")
        with open(conf.get_copying_path()) as l:
            info.SetLicence(l.read())
        
        wx.AboutBox(info)
        
    def sign_in(self):
        """ Authorize on vk.com """
        
        t = conf.get_token()  # try to get token from config
        
        # If user already got access token use it for authorization
        if t:
            # Try to get access
            auth = data.get_access(t)
            
            if auth[0]:
                # Login
                data.vkapi = auth[1]
            else:
                # Show error
                wx.MessageBox(auth[1], _("Error"), wx.OK | wx.ICON_ERROR)
                self.login = LoginDialog(self)
                self.login.ShowModal()
            
        # Else show Sign In dialog
        else:
            self.login = LoginDialog(self)
            self.login.ShowModal()
    
    def open_app_opts(self, event):
        """ Open app options dialog """        
        
        self.app_opts = OptionsDialog(self)
                    
        # Show dialog
        self.app_opts.ShowModal()
        
        if self.app_opts.values:
            self.min_close = self.app_opts.values["min_close"]
            self.switch_onclose_bind()
            
            self.overwrite_files = self.app_opts.values["overwrite"]
            
            old = self.sys_gtk_icons
            self.sys_gtk_icons = self.app_opts.values["icons"]
            if not self.sys_gtk_icons == old:
                self.update_bitmaps()
            
            if self.app_opts.values["ddir"]:
                self.download_dir = self.app_opts.values["ddir"]
    
    def load_params(self):
        """ Load few params from config file """
        
        params = conf.get_params()
        
        # Volume level
        self.volume_sl.SetValue(params["vol"])
        
        # Active tab
        if params["tab"]:
            self.notebook.SetSelection(params["tab"] - 1)
        
        # Minimize app to system tray if window closed
        self.min_close = params["minimize_on_close"]
        
        # Use system gtk icons
        self.sys_gtk_icons = params["sys_gtk_icons"]
        
        # Reverse
        if params["reverse"]:
            self.reverse = params["reverse"]  # set value
            self.play_menu_reverse.Check()  # check menu item
        
        # Random
        if params["random"]:
            self.random = params["random"]
            self.play_menu_random.Check()
        
        # Download directory
        self.download_dir = params["ddir"]
        
        # Overwrite exist files when downloading
        self.overwrite_files = params["overwrite_files"]
    
    def load_playlists(self):
        """ Load playlists from config file """
        
        for sec in conf.get_playlists():
            # Ignore app section
            if not sec == "app":
                
                # Get info about playlist
                info = conf.get_playlist_info(sec)
                audios = data.get_audios(info["id"], info["album"])
                
                if audios:
                    # Insert audios to main audios list
                    self.audios[sec] = audios["items"]
                    
                    # Add page
                    self.add_page(info["name"], info["pos"], self.audios[sec])
        
    def add_plst(self, event):
        """ Add new playlist """        
        
        self.new_plst = AddDialog(self)
        self.new_plst.ShowModal()
        
        # If audios got
        if self.new_plst.audios:
            
            # Add new playlist to self.audios
            n = conf.get_playlists_num()
            self.audios["playlist" + str(n)] = self.new_plst.audios["items"]
            
            name = self.decode_string(self.new_plst.plst)  
            
            # Add playlist to config
            conf.add_playlist(name, self.new_plst.plst_id, 
                              n, self.new_plst.album)
            
            # Add new page
            self.add_page(name, n, self.audios["playlist" + str(n)])
            
            conf.save_conf()
    
    def rm_plst(self, event):
        """ Remove playlist and page """
        
        # Index and name of currently select page
        page_i = self.notebook.GetSelection()
        page_name = self.notebook.GetPageText(page_i)
        
        # If it's some search result
        if page_name in self.search_results.values():
            
            # Get search_result
            for k in self.search_results:
                if self.search_results[k] == page_name:
                    n = k
            search_result = "search_result" + str(n)
            
            # If current playling audiotrack in this tab, stop playing
            if self.now_playing[3] == search_result:
                self.stop_playing(None)
                self.now_playing[3] = None
                
            self.audios.__delitem__(search_result)
        
        # If it's playlist
        else:
            page_name = self.decode_string(page_name)
            
            # Current playlist
            playlist = conf.get_playlist_section(page_name)
            
            # If current playling audiotrack in this playlist, stop playing
            if self.now_playing[3] == playlist:
                self.stop_playing(None)
                self.now_playing[3] = None
            
            # Remove playlist and save config
            self.audios.__delitem__(playlist)
            conf.rm_playlist(playlist)
            conf.save_conf()
    
    def open_search(self, event):
        """ Open search dialog """
        
        self.search_dlg = SearchDialog(self)
        
        # Show dialog
        self.search_dlg.ShowModal()
        
        # If something was found
        if self.search_dlg.audios:
            
            # Add new search results to self.audios
            k = self.search_results.keys()
            if len(k) > 0:
                k.sort()
                n = k[-1] + 1
            else:
                n = 0
            
            search_result = "search_result" + str(n)
            self.audios[search_result] = self.search_dlg.audios["items"]
            self.search_results[n] = self.search_dlg.query
            
            self.add_page(self.search_results[n], len(self.audios), 
                          self.audios["search_result" + str(n)], 
                          search_result=True)
        
    def add_page(self, name, pos, audio_lst, search_result=False):
        """ Add new page with playlist to AuiNotebook """
        
        # New panel (page)
        panel = ListCtrlPanel(self.notebook, wx.ID_ANY, wx.DefaultPosition, 
                              wx.DefaultSize, wx.TAB_TRAVERSAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        list_ctrl = wx.ListCtrl(panel, wx.ID_ANY, wx.DefaultPosition, 
                                wx.DefaultSize, 
                                wx.LC_REPORT | wx.LC_SINGLE_SEL)
        
        # Space available for list_ctrl = 
        # frame's clientsize width - borders
        lc_space = self.GetClientSize().GetWidth() - 15
        
        # Colums width
        num_w = lc_space / 12  # N col width
        dur_w = lc_space / 9  # Duration col width
        # Artist & Title cols width
        main_w = (lc_space - (num_w + dur_w )*1.5) / 2
        
        list_ctrl.InsertColumn(0, _("N"), width=num_w)
        list_ctrl.InsertColumn(1, _("Artist"), width=main_w)
        list_ctrl.InsertColumn(2, _("Title"), width=main_w)
        list_ctrl.InsertColumn(3, _("Duration"), width=dur_w)
        
        # Add tracks to list_ctrl
        i = 0
        for item in audio_lst:
            
            # Audio track duration
            dur = wx.TimeSpan.Seconds(item["duration"])
            
            list_ctrl.InsertStringItem(i, str(i+1))  # N
            list_ctrl.SetStringItem(i, 1, item["artist"])
            list_ctrl.SetStringItem(i, 2, item["title"])
            list_ctrl.SetItemData(i, i)
                        
            # Duratuion > 1 hour, write with hours
            if dur.GetHours() > 0:
                _dur = dur.Format("%H:%M:%S")
            else:
                _dur = dur.Format("%M:%S")
            list_ctrl.SetStringItem(i, 3, _dur)
            
            # Add audiotrack info to itemDataMap for column sorter
            panel.itemDataMap[i] = (i+1, item["artist"], item["title"], _dur)
            
            i += 1
        
        # ListCtrl sorting
        panel.init_column_sorter()

        sizer.Add(list_ctrl, 1, wx.ALL | wx.EXPAND, 5 )
        panel.SetSizer(sizer)
        
        # Insert page to notebook
        name = self.decode_string(name)
        self.notebook.InsertPage(pos, panel, name, True)
        
        # --- Events --- #
        # Play activated item (double click or enter)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.start_playing)
        # Update id of now playing audiotrack if list sorted
        self.Bind(wx.EVT_LIST_COL_CLICK, self.update_track_i)
        
        # Message to statusbar
        # If search results
        if search_result:
            self.statusbar.SetStatusText(_("Added search results for %s") 
                                            % name)
        # If playlist
        else:
            self.statusbar.SetStatusText(_("Playlist %s successfully added") 
                                            % name)
        
    def set_volume(self, event):
        """ Volume regulation by volume slider """        
        
        vol = self.volume_sl.GetValue() / 100.0 
        self.media.SetVolume(vol)
        
    def mute_volume(self, event):
        """ Mute / Unmute volume by button """
        
        # Mute
        if self.media.GetVolume() > 0:
            self.media.SetVolume(0)
            self.muted = True
            self.volume_btn.SetBitmapLabel(self.vol_off_bitmap)
        # Unmute
        else:
            vol = self.volume_sl.GetValue() / 100.0
            self.media.SetVolume(vol)
            self.muted = False
            self.volume_btn.SetBitmapLabel(self.vol_on_bitmap)
    
    def upd_progress_slider(self, event):
        """ Update value on progress slider while audiotrack playing """
        
        # Update progress slider
        i = self.media.Tell()
        self.progress_sl.SetValue(i)
        self.progress_sl.GetValue()
        
    def scroll_progress(self, event):
        """ Scroll audiotrack with progress slider """
        
        i = self.progress_sl.GetValue()
        self.media.Seek(i)
        
    def highlight_item(self):
        """ Highlight item in ListCtrl """
        
        # Selected items background
        bg_col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUHILIGHT)
        # Selected items font color
        fnt_col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
            
        # Get Panel with ListCtrl from page
        panel = self.notebook.GetPage(self.now_playing[0]).GetChildren()
        
        # Set colors
        panel[0].SetItemBackgroundColour(self.now_playing[1], bg_col)
        panel[0].SetItemTextColour(self.now_playing[1], fnt_col)
        
    def unhighlight_item(self, i):
        """ Remove highlight from ListCtrl item """
        
        # ListBox-like items background
        bg_col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        # ListBox-like items font color
        fnt_col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        
        # Get Panel with ListCtrl from page
        panel = self.notebook.GetPage(self.now_playing[0]).GetChildren()
        
        # Set colors
        panel[0].SetItemBackgroundColour(i, bg_col)
        panel[0].SetItemTextColour(i, fnt_col)
    
    def decode_string(self, s):
        """ 
        If any problems with string decoding/encoding, 
        then need to set correct encoding for it 
        """
        
        try:
            s.decode()
        except UnicodeDecodeError:
            s = s.decode(self.locale.GetSystemEncodingName())
        except UnicodeEncodeError:
            s = s.encode(self.locale.GetSystemEncodingName())
        
        return s
        
    def get_playlist_key(self, page_name):
        """ Get playlist's key for self.audios by page name """
        
        # If audiotrack from search results
        if page_name in self.search_results.values():
            
            # Get search_result
            for k in self.search_results:
                if self.search_results[k] == page_name:
                    sn = k
            playlist = "search_result" + str(sn)
        
        # If from playlists    
        else: 
            # Current playlist's list of dicts with audiotracks info
            page_name = self.decode_string(page_name)
            playlist = conf.get_playlist_section(page_name)
            
        return page_name, playlist
    
    def get_track_i(self, _next=None, _prev=None, _rand=None):
        """ Get index of audiotrack """
        
        # Index of currently select page
        i = self.notebook.GetSelection()
        
        # Panel from current notebook page (opened tab)
        panel = self.notebook.GetPage(i).GetChildren()
        
        # Get item index
        # If next
        if _next:
            
            item_i = self.now_playing[1]
            
            # Check next
            if (item_i + 1) < len(self.audios[self.now_playing[3]]):
                # Current
                cur_item_i = self.now_playing[1]
                # Next
                item_i += 1
            # Get first track index if last recently played
            else:
                cur_item_i = len(self.audios[self.now_playing[3]]) - 1
                item_i = 0
        
        # If prev       
        elif _prev:
            item_i = self.now_playing[1]
            
            if (item_i - 1) >= 0:
                cur_item_i = self.now_playing[1]
                item_i -= 1
            else:
                cur_item_i = 0
                item_i = len(self.audios[self.now_playing[3]]) - 1
        
        # If random
        elif _rand:
            
            cur_item_i = self.now_playing[1]
            item_i = data.get_rand_i(len(self.audios[self.now_playing[3]]) - 1)
        
        # If selected    
        else:
            # Selected ListCtrl item
            item_i = panel[0].GetNextItem(-1, wx.LIST_NEXT_ALL, 
                                          wx.LIST_STATE_SELECTED)
        
        # With wxPython 2.8 GetItemText(-1) work as GetItemText(0)
        # but with 3.0.2 it make an error
        if item_i < 0:
            item_i = 0
        
        # Get track number
        track_n = panel[0].GetItemText(item_i)
        if track_n:
            track_n = int(track_n) - 1
        else:
            track_n = 0
        
        if _next or _prev or _rand:
            return track_n, item_i, cur_item_i
        else:
            return track_n, item_i
    
    def update_track_i(self, event):
        """ Update audiotrack id """
        
        if self.now_playing[3]: 
        
            # Index of currently select page
            i = self.notebook.GetSelection()         
            
            # Panel from current notebook page (opened tab)
            panel = self.notebook.GetPage(i).GetChildren()                
            
            count = len(self.audios[self.now_playing[3]])
            for line in range(count):
                
                # Get N
                track_n = panel[0].GetItemText(line)
                
                # If Numbers are similar
                if (int(track_n) - 1) == self.now_playing[2]:
                    
                    # Update index
                    self.now_playing[1] = line
        
        else:
            event.Skip()
    
    def start_playing(self, event):
        """ Play audiotracks """
              
        self.play = True
        self.play_btn.SetBitmapLabel(self.pause_bitmap)
        
        # If some item was highlited clear it
        try:
            self.unhighlight_item(self.now_playing[1])
        except AttributeError:
            pass
                
        # Index and name of currently select page
        page_i = self.notebook.GetSelection()   
        page_name = self.notebook.GetPageText(page_i)
        
        # Selected track N and index
        n, i = self.get_track_i()
        
        # Get playlist's key
        page_name, playlist = self.get_playlist_key(page_name)
        
        cur_track = self.audios[playlist][n]
        
        # Load and play
        name = "%s - %s" % (cur_track["artist"], cur_track["title"])
        self.now_playing = [page_i, i, n, playlist]
        self.play_track(cur_track["url"], name, cur_track["duration"])
        
        # Highlight audiotrack
        self.highlight_item()
        
    def stop_playing(self, event):
        """ Stop audios playing """
        
        self.play = False
        
        # Stop timer and playing
        self.timer.Stop()
        self.media.Stop()
        
        # Set sliders values to 0
        self.progress_sl.SetValue(0)
        self.progress_sl.SetRange(0, 0)
        
        self.taskbar.SetIcon(self.taskbar.icon, "wx VK Music")
        self.play_btn.SetBitmapLabel(self.play_bitmap)
        self.unhighlight_item(self.now_playing[1])
        
    def play_pause(self, event):
        """ Set pause / remove pause """
        
        # If playing already started
        if self.play:
            
            # Continue playing (unset pause)
            if self.pause:
                self.pause = False
                self.timer.Start(100)
                self.media.Play()
                self.play_btn.SetBitmapLabel(self.pause_bitmap)
            # Set pause
            else:
                self.pause = True
                self.timer.Stop()
                self.media.Pause()
                self.play_btn.SetBitmapLabel(self.play_bitmap)
        
        # Else just start it        
        else:
            self.start_playing(None)
        
    def play_next(self, event):
        """ Play next audiotrack from playlist """
        
        # Num (int) of EVT_BUTTON type
        btn_pressed = wx.EVT_BUTTON._getEvtType()
        
        if self.now_playing[3]:
            
            # Play next if playing not on repeat elif next button pressed
            if not self.repeat or event.GetEventType() == btn_pressed:
                # Get next audiotrack N and index; current audiotrack index
                next_n, next_i, cur_i = self.get_track_i(_next=True)
                self.now_playing[1] = next_i  # index
                self.now_playing[2] = next_n  # N
            
            next_track = self.audios[self.now_playing[3]][self.now_playing[2]]
            
            # Load and Play
            name = "%s - %s" % (next_track["artist"], next_track["title"])
            self.play_track(next_track["url"], name, next_track["duration"])
            
            if not self.repeat or event.GetEventType() == btn_pressed:
                # Highlight next audiotrack
                self.unhighlight_item(cur_i)
                self.highlight_item()
            
        else:
            self.start_playing(None)
        
    def play_prev(self, event):
        """ Play previous audiotrack from playlist """      
        
        # Num (int) of EVT_BUTTON type
        btn_pressed = wx.EVT_BUTTON._getEvtType()        
        
        if self.now_playing[3]:
            
            # Play next if playing not on repeat elif next button pressed
            if not self.repeat or event.GetEventType() == btn_pressed:
                # Get prev audiotrack N and index; current audiotrack index
                prev_n, prev_i, cur_i = self.get_track_i(_prev=True)
                self.now_playing[1] = prev_i  # index
                self.now_playing[2] = prev_n  # N
                
            prev_track = self.audios[self.now_playing[3]][self.now_playing[2]]
            
            # Load and Play
            name = "%s - %s" % (prev_track["artist"], prev_track["title"])
            self.play_track(prev_track["url"], name, prev_track["duration"])
            
            if not self.repeat or event.GetEventType() == btn_pressed:
                # Highlight next audiotrack
                self.unhighlight_item(cur_i)
                self.highlight_item()
            
        else:
            self.start_playing(None)
    
    def play_random(self, event):
        """ Play random audiotrack from current playlist """
        
        # Num (int) of EVT_BUTTON type
        menu_item_pressed = wx.EVT_MENU._getEvtType()        
        
        if self.now_playing[3]:
            
            # Play if playing not on repeat elif random menu item pressed
            if not self.repeat or event.GetEventType() == menu_item_pressed:
                # Get random audiotrack N and index; current audiotrack index
                rand_n, rand_i, cur_i = self.get_track_i(_rand=True)
                self.now_playing[1] = rand_i  # index
                self.now_playing[2] = rand_n  # N
                
            rand_track = self.audios[self.now_playing[3]][self.now_playing[2]]
            
            # Load and Play
            name = "%s - %s" % (rand_track["artist"], rand_track["title"])
            self.play_track(rand_track["url"], name, rand_track["duration"])
            
            if not self.repeat or event.GetEventType() == menu_item_pressed:
                # Highlight next audiotrack
                self.unhighlight_item(cur_i)
                self.highlight_item()
            
        else:
            self.start_playing(None)
    
    def switch_repeat(self, event):
        """ Turn on/off repeat mode """
        
        if self.repeat:
            self.repeat = False
        else:
            self.repeat = True
    
    def switch_random(self, event):
        """ Turn on/off playlist playing in random order """
        
        # Unbind
        self.Unbind(wx.media.EVT_MEDIA_FINISHED)        
        
        if self.reverse:
            self.reverse = False
            self.play_menu_reverse.Check(False)
        
        if self.random:
            self.random = False
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_next)
        else:
            self.random = True
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_random)
    
    def switch_reverse(self, event):
        """ Turn on/off playlist reverse playing """
                
        # Unbind
        self.Unbind(wx.media.EVT_MEDIA_FINISHED)
        
        if self.random:
            self.random = False
            self.play_menu_random.Check(False)
                        
        if self.reverse:
            # Turn off and bind play_next 
            self.reverse - False
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_next)
        else:
            # Turn on and bind play_prev
            self.reverse = True
            self.Bind(wx.media.EVT_MEDIA_FINISHED, self.play_prev)
    
    def play_track(self, url, name, dur):
        """ Load and play audiotrack """
        
        # Load audiotrack
        self.media.LoadURI(url)
        
        # Get audiotrack lenght
        duration = self.media.Length()
        
        # Sometimes lenght got == 0 (wxPython bug?), if that happens 
        # use duration value from vk.com * 1000 (secs => milisecs)
        if not duration:
            duration = dur * 1000
        
        # Set audiotrack's lenght to progress slider
        self.progress_sl.SetRange(0, duration)
        # Start timer and play
        self.timer.Start(100)
        self.media.Play()
        
        if not self.muted:
            self.set_volume(None)
        
        # Set "Playing: Artist - Title" as statusbar text 
        # and taskbaricon tooltip
        self.statusbar.SetStatusText(_("Playing: %s") % name)
        self.taskbar.SetIcon(self.taskbar.icon, _("Playing: %s") % name)    
     
    def create_downloader(self):
        """ Create downloader """
        
        self.downloader = DownloaderDialog(self)
    
    def check_downloader(self):
        """ Check does downloader already created, if than no create it """
        
        if not self.downloader:
            self.create_downloader()
    
    def show_downloader(self, event):
        """ Show downloader frame """
        
        self.check_downloader()
        if not self.downloader.IsShown():
            self.downloader.Show(True)
        
    def download_selected(self, event):
        """ Download selected audiotrack """
        
        # Index and name of currently select page
        page_i = self.notebook.GetSelection()   
        page_name = self.notebook.GetPageText(page_i)
        
        # Selected track N and index
        n, i = self.get_track_i()
        
        page_name, playlist = self.get_playlist_key(page_name)
        
        # Get selected track 
        sel_track = self.audios[playlist][n]
        track_name = " - ".join([sel_track["artist"], sel_track["title"]])
        
        # Check downloader and download queue
        self.check_downloader()
        
        # Add it to download queue
        self.downloader.add_to_queue(track_name, sel_track["url"])
        
        # Start downloading
        self.downloader.download_start()
    
    def download_playing(self, event):
        """ Download playing audiotrack """
        
        # If nothing playing skip event
        if not self.now_playing[3]:
            event.Skip()
        else:
            # Get playing audiotrack
            cur_track = self.audios[self.now_playing[3]][self.now_playing[2]]
            track_name = " - ".join([cur_track["artist"], cur_track["title"]])
            
            # Check downloader and download queue
            self.check_downloader()
            
            # Add it to download queue
            self.downloader.add_to_queue(track_name, cur_track["url"])
            
            # Start downloading
            self.downloader.download_start()
            
    def download_playlist(self, event):
        """ Fully download playlist from currently active tab """
        
        # Index and name of currently select page
        page_i = self.notebook.GetSelection()   
        page_name = self.notebook.GetPageText(page_i)        
        
        page_name, playlist = self.get_playlist_key(page_name)
        
        # Check downloader and download queue
        self.check_downloader()        
        
        # Add all tracks from playlist to download queue
        for track in self.audios[playlist]:
            track_name = " - ".join([track["artist"], track["title"]])
            self.downloader.add_to_queue(track_name, track["url"])
        
        # Start downloading
        self.downloader.download_start()
    
    def key_pressing(self, event):
        """ Do some action if binded key pressed """
        
        keycode = event.GetKeyCode()
        ctrl_key = event.CmdDown()
        
        # Play / Pause
        if keycode == wx.WXK_SPACE:
            self.play_pause(None)            
        # Prev
        elif keycode == wx.WXK_LEFT and ctrl_key:
            self.play_prev(None)
        # Next
        elif keycode == wx.WXK_RIGHT and ctrl_key:
            self.play_next(None)
    
class ListCtrlPanel(wx.Panel, mixlc.ColumnSorterMixin):
    """ Panel for pages with playlists """
    
    def __init__(self, *args, **kwargs):
        super(ListCtrlPanel, self).__init__(*args, **kwargs)
        
        self.itemDataMap = {}  # dict for column sorter
    
    def init_column_sorter(self):
        mixlc.ColumnSorterMixin.__init__(self, 4)
        
    def GetListCtrl(self):
        """ Method needed by ColumnSorterMixin. Return list_ctrl """        
        
        return self.GetChildren()[0]

class LoginDialog(wx.Dialog):
    """ Dialog for signin. User need to enter login and password """    
    
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        """ Load interface """
        
        self.SetTitle(_("Sign In"))
        self.make_layout()
        self.SetInitialSize()
        
        # Events
        self.Bind(wx.EVT_CLOSE, self.quit_dial)
        self.Bind(wx.EVT_CHECKBOX, self.show_passwd, self.show_passwd_cb)
        self.sign_btn.Bind(wx.EVT_BUTTON, self.sign_in, self.sign_btn)
    
    def make_layout(self): 
        
        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Static texts --- #
        # Login text
        login_text = wx.StaticText(self, wx.ID_ANY, _("Login (email / Tel.)"), 
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        login_text.Wrap(-1)
        
        # Password text
        passwd_text = wx.StaticText(self, wx.ID_ANY, _("Password"), 
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        passwd_text.Wrap(-1)
        
        # --- Text ctrls --- #
        # Login
        self.login_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                      wx.DefaultPosition, wx.DefaultSize, 0)
        lg = conf.get_login()  # try to get login from config
        if lg:
            self.login_ctrl.SetValue(lg)
            
        # Password
        # Create two text ctrls with and without wx.TE_PASSWORD 
        # Ctrls will be show/hide by checkbox 
        self.passwd_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                       wx.DefaultPosition, wx.DefaultSize, 
                                       wx.TE_PASSWORD)
        self._passwd_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, 
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self._passwd_ctrl.Hide()
        
        # --- CheckBoxes --- #
        # Show/hide password checkbox
        self.show_passwd_cb = wx.CheckBox(self, wx.ID_ANY, _("Show password"), 
                                          wx.DefaultPosition, wx.DefaultSize, 
                                          0)
        
        # Save email checkbox
        self.save_login_cb = wx.CheckBox(self, wx.ID_ANY, _("Save login"), 
                                         wx.DefaultPosition, wx.DefaultSize, 0)
        self.save_login_cb.SetValue(True)  # checked by default

        # Save access_token
        self.save_token_cb = wx.CheckBox(self, wx.ID_ANY, _("Save session"), 
                                         wx.DefaultPosition, wx.DefaultSize, 0)
        self.save_token_cb.SetValue(True)  # checked by default
        
        # --- Buttons --- #
        # SignIn button                          
        self.sign_btn = wx.Button(self, wx.ID_ANY, _("Sign In"), 
                                  wx.DefaultPosition, wx.DefaultSize, 0)
                          
        # Add widgets to sizer
        sizer.AddMany([
            (login_text, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.login_ctrl, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 3),
            (passwd_text, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.passwd_ctrl, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 3),
            (self._passwd_ctrl, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 3),
            (self.show_passwd_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.save_login_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.save_token_cb, 0, wx.ALIGN_CENTER | wx.ALL, 5),
            (self.sign_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        ])
        
        self.SetSizer(sizer)
        self.Layout()
    
    def show_passwd(self, event):
        """ Show/hide password """
        
        if self.show_passwd_cb.GetValue():
            # Copy value
            self._passwd_ctrl.SetValue(self.passwd_ctrl.GetValue())
            self.passwd_ctrl.Hide()  # hide ctrl with wx.TE_PASSWORD
            self._passwd_ctrl.Show()  # show ctrl without wx.TE_PASSWORD
            # Re-layout for placing _passwd_ctrl to passwd_ctrl's pos
            self.Layout()
        else:
            self.passwd_ctrl.SetValue(self._passwd_ctrl.GetValue())
            self._passwd_ctrl.Hide()
            self.passwd_ctrl.Show()
    
    def sign_in(self, event):
        """ Get login and password """
        
        # Get info
        self.login = self.login_ctrl.GetValue()
        if self._passwd_ctrl.IsShown():
            self.passwd = self._passwd_ctrl.GetValue()
        else:
            self.passwd = self.passwd_ctrl.GetValue()
        
        # Authorize
        auth = data.login_to_vk(self.login, self.passwd)
        if auth[0]:
            data.vkapi = auth[1]      
            
            # Save user's login
            if self.save_login_cb.GetValue():            
                conf.save_login(self.login_ctrl.GetValue())
                
            # Save access token
            if self.save_token_cb.GetValue():
                conf.save_token(data.vkapi.access_token)
            
            # Save changes
            conf.save_conf()           
            
            # Destroy dialog
            self.Destroy()
        else:
            # Show error message
            wx.MessageBox(auth[1], _("Error"), wx.OK | wx.ICON_ERROR)        
    
    def quit_dial(self, event):
        """ Show quit dialog """
        
        msg = _("Login on vk.com required. Are you sure to quit this dialog?")
        dial = wx.MessageDialog(self, msg, _("Question"), 
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        # Get user's answer
        res = dial.ShowModal()
        if res == wx.ID_YES:
            self.Destroy()
        else:
            event.Veto()  # ignore event
        
def main():
    
    # Read configuration file
    conf.read_conf()
    # Run
    app = wx.App()
    MainFrame(None)
    app.MainLoop()
