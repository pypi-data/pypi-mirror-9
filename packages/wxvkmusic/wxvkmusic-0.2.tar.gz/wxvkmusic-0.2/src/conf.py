#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
# wx VK Music 
# Free & OpenSource music player for vk.com social network
# https://bitbucket.org/xxblx/wx-vk-music
# 
# Oleg Kozlov (xxblx), 2014 - 2015
###########################################################

import os
import sys
from re import findall, sub
from ConfigParser import SafeConfigParser

# Config parser
prs = SafeConfigParser()

def get_conf_dir():
    """ Return path to directory where will be saved app's config """ 
    
    conf_dir = ""
    
    # If Linux
    # App save config in XDG_CONFIG_HOME dir from XDG Base Directory spec
    # http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    if os.name == "posix":
        if os.getenv("XDG_CONFIG_HOME"):
            conf_dir = os.path.join(os.getenv("XDG_CONFIG_HOME"), "wxvkmusic")
        else:
            conf_dir = os.path.join(os.path.expanduser("~"), 
                                    ".config/wxvkmusic")
    # If windows: User\wxvkmusic
    else:
        conf_dir = os.path.join(os.path.expanduser("~"), "wxvkmusic")
    
    # Make dir
    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
    
    return conf_dir
    
def read_conf():
    """ Read configuration from file """
    
    f = os.path.join(get_conf_dir(), "config.ini")  # config's path
    
    count = None    
    
    if not os.path.exists(f):
        # Write to file
        with open(f, "w") as config_file:         
            config_file.write("[app]")
            config_file.write("")
    else:
        # Update sections nums
        count, data = update_sec_nums(f)
        with open(f, "w") as config_file:
            config_file.write(data)
        
    # Read
    prs.read(f)  
    
    if count:
        prs.set("app", "playlists", str(count))

def save_conf():
    """ Save changes to configuration file """
    
    f = os.path.join(get_conf_dir(), "config.ini")  # config's path
    
    # Write to file
    with open(f, "w") as config_file:
        prs.write(config_file)

def save_token(t):
    """ Save access token to config """
    
    prs.set("app", "access_token", t)
    
def get_token():
    """ Get access token from config """
    
    if prs.has_option("app", "access_token"):
        return prs.get("app", "access_token")
    else:
        return False

def save_login(l):
    """ Save user's login """
    
    prs.set("app", "login", l)
    
def get_login():
    """ Get user's login from config """
    
    if prs.has_option("app", "login"):
        return prs.get("app", "login")
    else:
        return False
        
def get_playlists_num():
    """ Get number of added playlists from config """
    
    if prs.has_option("app", "playlists"):
        return prs.getint("app", "playlists")
    else:
        prs.set("app", "playlists", "0")
        return 0

def get_playlists():
    """ Get list with playlists sections names """
    
    return prs.sections()
    
def get_playlist_info(s):
    """ Get details about playlist from config """
    
    name = prs.get(s, "name")
    _id = prs.get(s, "id")
    pos = prs.getint(s, "pos")
    
    if prs.has_option(s, "album"):  # if has album
        album = prs.get(s, "album")
    else:
        album = False
    
    # Return dict
    return {"name": name, "id": _id, "pos": pos, "album": album}
    
def get_playlist_section(n):
    """ Get name of playlist's section in config by page's name """
    
    for sec in prs.sections():
        if not sec == "app" and prs.get(sec, "name") == n:
            return sec
        
def add_playlist(name, i, pos, album=False):
    """ Add new playlist to config """
    
    # Number of already added playlists
    n = get_playlists_num()
        
    # Section name
    sec = "playlist" + str(n)
    
    # Add new section about new playlist
    prs.add_section(sec)
    
    prs.set(sec, "name", name)  # playlist name
    prs.set(sec, "id", i)  # playlist id
    prs.set(sec, "pos", str(pos))  # playlist pos
    
    if album:
        prs.set(sec, "album", album)  # album id
    
    # +1 to app - playlists
    prs.set("app", "playlists", str(n + 1))
    
def rm_playlist(sec_name):
    """ Remove playlist from config """
    
    # Remove section
    prs.remove_section(sec_name)

def save_params(vol, tab, min_close, icons, rev, rand, ddir, owf):
    """ Save app params """
    
    prs.set("app", "volume", str(vol))  # volume level
    prs.set("app", "last_tab", str(tab))  # last opened tab
    prs.set("app", "minimize_on_close", str(min_close))  # last opened tab
    prs.set("app", "sys_gtk_icons", str(icons))  # use sys gtk icons
    prs.set("app", "reverse", str(rev))  # reverse playlist playing
    prs.set("app", "random", str(rand))  # random playlist playing
    prs.set("app", "download_dir", ddir)  # download directory
    prs.set("app", "overwrite_files", str(owf))  # overwrite files
    
def get_params():
    """ Get app params """
    
    params = {}    
    
    # Volume
    if prs.has_option("app", "volume"):
        params["vol"] = prs.getint("app", "volume")
    else:
        params["vol"] = 100
    
    # Last tab
    if prs.has_option("app", "last_tab"):
        # +1 because 0 == False on the if else block at ui.load_params
        params["tab"] = prs.getint("app", "last_tab") + 1 
    else:
        params["tab"] = False
        
    # Minize app window on close; Reverse; Random; Use system gtk icons
    for param in ["minimize_on_close", "reverse", "random", "sys_gtk_icons"]:
        if prs.has_option("app", param):
            params[param] = prs.getboolean("app", param)
        else:
            params[param] = False
        
    # Download dir
    if prs.has_option("app", "download_dir"):
        params["ddir"] = prs.get("app", "download_dir")
    else:
        params["ddir"] = os.path.expanduser("~")
        
    # Overwrite exist files when downloading
    if prs.has_option("app", "overwrite_files"):
        params["overwrite_files"] = prs.getboolean("app", "overwrite_files")
    else:
        params["overwrite_files"] = True
    
    return params

def update_sec_nums(f):
    
    # Read
    with open(f, "r") as conf_file:
        data = conf_file.read()
        
        # Find added sections
        secs = findall("playlist\d+", data)
        
        count = 0 
        for i in secs:
            # Replace number in section name
            data = sub(i, "playlist" + str(count), data)
            count += 1
    
    return count, data

def get_icon_path(f):
    """ Return absolute path to icon file """
    
    if os.name == "posix":
        d = os.path.join(sys.prefix, "share/wxvkmusic")
        return os.path.join(d, f)

def get_copying_path():
    """ Return path to COPYING file """
    
    if os.name == "posix":
        d = os.path.join(sys.prefix, "share/wxvkmusic")
        return os.path.join(d, "COPYING")

def get_locale_path():
    """ Return path to locale dir (like /usr/share/locale) """
    
    if os.name == "posix":
        return os.path.join(sys.prefix, "share/locale")
