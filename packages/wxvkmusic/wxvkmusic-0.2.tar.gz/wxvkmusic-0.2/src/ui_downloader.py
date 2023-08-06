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
import requests
from Queue import Queue
from threading import Thread
from re import sub, findall, UNICODE
from os.path import join, exists

_ = wx.GetTranslation

ID_DOWNLOADING = wx.NewId()
ID_DOWNLOAD_COMPLETE = wx.NewId()

def EVT_DOWNLOADING(w, func):
    """ Define DownloadingEvent """
    
    w.Connect(-1, -1, ID_DOWNLOADING, func)
    
def EVT_DOWNLOAD_COMPLETE(w, func):
    """ Define DownloadCompleteEvent """
    
    w.Connect(-1, -1, ID_DOWNLOAD_COMPLETE, func)
    
class DownloadingEvent(wx.PyEvent):
    """ Event used for access to downloading progress """
    
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        
        self.SetEventType(ID_DOWNLOADING)
        self.data = data
        
class DownloadCompleteEvent(wx.PyEvent):
    """ Event used to mark current downloading as complete """
    
    def __init__(self):
        wx.PyEvent.__init__(self)
        
        self.SetEventType(ID_DOWNLOAD_COMPLETE)

class DownloaderDialog(wx.Dialog):
    """ Audiotracks downloader dialog """
    
    def __init__(self, parent):
        super(DownloaderDialog, self).__init__(parent)
        
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        
        self.SetSize((600, 270))  # size    
        self.SetTitle("wx VK Music Downloader")  # frame's title
        self.Centre()  # move to center of screen

        # Downloading queue
        self.queue = Queue()
        
        self.download_now = False
        self.last_id = -1
        self.overwrite_files = self.parent.overwrite_files
        
        self.make_layout()
        
        # Events
        self.Bind(wx.EVT_CLOSE, self.close_frame)
        EVT_DOWNLOADING(self, self.upd_download_progress)
        EVT_DOWNLOAD_COMPLETE(self, self.download_complete)
    
    def make_layout(self):
        
        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)  
            
        # Download progress gauge
        self.dl_gauge = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, 
                                 wx.DefaultSize, wx.GA_HORIZONTAL)
        self.dl_gauge.SetValue(0)
        
        # ListCtrl with downloading queue
        self.list_ctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition,
                                     wx.DefaultSize, wx.LC_REPORT)
        col_width = self.GetClientSize().GetWidth() - 10
        self.list_ctrl.InsertColumn(0, _("Download queue"), width=col_width)
        
        sizer.AddMany([
            (self.dl_gauge, 0, wx.EXPAND | wx.ALL, 5),
            (self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        ])
        
        self.SetSizer(sizer)
        self.Layout()
        
    def close_frame(self, event):
        """ Closing frame """
        
        # If something downloading just hide frame
        if self.download_now:
            self.Show(False)
        # If all downloads are complete destroy frame
        else:
            self.Destroy()
            self.parent.downloader = None
            
    def upd_download_progress(self, event):
        """ Update loading on dwonload progress gauge """
        
        if event.data:
            self.dl_gauge.SetValue(event.data)
            
    def get_file_size(self, link):
        """ Get file size in int Bytes and in float MBs """
        
        head = requests.head(link)
        self.size = int(head.headers["content-length"])
        self.mbs_size = float(head.headers["content-length"]) / 104857
    
    def add_to_queue(self, track_name, link):
        """ Add audiotrack to downloads queue """
        
        # Save only letters, digits, _, -, (), [] in track_name
        # and delete any other symbols
        # Because re.sub in anyway (with/without re.UNICODE)
        # will replace cyrillic as not-letters, used re.findall first
        for i in findall("[^\w\.\-\s\[\]\(\)]", track_name, UNICODE):
            track_name = sub("\\" + i, "_", track_name, UNICODE)
            
        # Add track to queue
        item = wx.ListItem()
        item.SetText(track_name)
        item.SetId(self.last_id + 1)
        self.last_id += 1
        self.list_ctrl.InsertItem(item)
        self.queue.put([track_name, link])

    def download_start(self):
        """ Start downloading """
        
        # If not downloading now start downloading
        if not self.download_now:
            if not self.IsShown():
                self.Show(True)
            self.download_now = True
            self.download_process()
    
    def download_process(self):
        """ Start/Continue/Complete downloading process """
        
        if not self.queue.empty():
            
            # Get item from queue 
            track = self.queue.get(block=True)
            
            self.get_file_size(track[1])
            self.dl_gauge.SetRange(self.size)
            
            # Download file
            path = join(self.parent.download_dir, track[0] + ".mp3")    
            DownloadThread(self, path, track[1])
            
        else:
            self.download_now = False
            self.last_id = -1
            
    def download_complete(self, event):
        """ Current downloading complete """
        
        # Delete previous downloaded audiotrack from ListCtrl
        self.list_ctrl.DeleteItem(0)
        
        # Continue downloading process
        self.download_process()
        
class DownloadThread(Thread):
    """ Download Thread """
    
    def __init__(self, parent, path, link):
        Thread.__init__(self)
        
        self.parent = parent
        self.path = path
        self.link = link
        
        self.start()
        
    def run(self):
        """ This method executes with self.start() """
        
        progress = 0  # downloaded bytes
        
        # Get audiotrack
        data = requests.get(self.link, stream=True)
        
        # Save audiostrack to local file
        if self.parent.overwrite_files or (not exists(self.path)):
            with open(self.path, "w") as f:
                for i in data.iter_content(chunk_size=1024):
                    if i:
                        f.write(i)
                        f.flush()
                        progress += len(i)
                        wx.PostEvent(self.parent, DownloadingEvent(progress))
        
        # Mark downloading proccess as complete
        self.parent.queue.task_done()
        wx.PostEvent(self.parent, DownloadCompleteEvent())
