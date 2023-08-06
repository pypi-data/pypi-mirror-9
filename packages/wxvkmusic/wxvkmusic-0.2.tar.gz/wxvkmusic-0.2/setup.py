#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
# wx VK Music 
# Free & OpenSource music player for vk.com social network
# https://bitbucket.org/xxblx/wx-vk-music
# 
# Oleg Kozlov (xxblx), 2014 - 2015
###########################################################

import sys
from distutils.core import setup
from distutils.command.install_data import install_data
from os import listdir, walk
from os.path import splitext, join
from subprocess import call

# Dict with pathes
DESTDIR = {
    "applications": join("share", "applications"),
    "wxvkmusic": join("share", "wxvkmusic"),
    "pixmaps": join("share", "pixmaps")
}

class DataInstaller(install_data):
    """ Class for installing app data """
    
    def run(self):
        install_data.run(self)
        
        # Update desktop-files db
        if sys.platform.startswith("linux"):
            try:
                call(["update-desktop-database"])
            except:
                print("ERROR: unable to update desktop database")

def create_mo():
    """ Build mo files from po in locale/lang/LC_MESSAGES dir """
    
    for dirpath, dirs_names, files_names in walk("locale"):
        for f in files_names:
            if splitext(f)[1] == ".po":
                fmo = splitext(f)[0] + ".mo"
                # Command like 
                # msgfmt locale/en/LC_MESSAGES/wxvkmusic.po \
                # -o locale/en/LC_MESSAGES/wxvkmusic.mo 
                c = ["msgfmt", join(dirpath, f), "-o", join(dirpath, fmo)]
                call(c)

def get_data_files():
    """ Return list with app data files """
    
    # Desktop file
    data = [(DESTDIR["applications"], ["wxvkmusic.desktop"])]
    
    # Data to wxvkmusic dir (like /usr/share/wxvkmusic)
    # Actions icons (play, stop, etc...) & taskbar icon
    share_wxvkmusic = [] 
    for i in listdir("icons"):
        if splitext(i)[1] == ".png" and splitext(i)[0] != "wxvkmusic":
            share_wxvkmusic.append(join("icons", i))
            
    # License text
    share_wxvkmusic.append("COPYING")
    
    data.append((DESTDIR["wxvkmusic"], share_wxvkmusic))
    
    # Locale
    for dirpath, dirs_names, files_names in walk("locale"):
        for f in files_names:
            if splitext(f)[1] == ".mo":
                data.append((join("share", dirpath), [join(dirpath, f)]))
                     
    # Pixmap for desktop file
    data.append((DESTDIR["pixmaps"], [join("icons", "wxvkmusic.png")]))
    
    return data

CMD = {"install_data": DataInstaller}

# gettext        
if sys.platform.startswith("linux"):
    create_mo()

setup(
    name = "wxvkmusic",
    version = "0.2",
    license = "GNU General Public License v3 or later (GPLv3+)",
    
    author = "Oleg Kozlov (xxblx)",
    author_email = "xxblx.oleg@yandex.com",
    
    url = "https://bitbucket.org/xxblx/wx-vk-music",
    
    description = "Free & OpenSource music player for vk.com social network",
    
    requires = ["wxPython", "vk", "requests"],

    packages = ["wxvkmusicapp"],
    package_dir = {"wxvkmusicapp": "src"},

    data_files = get_data_files(),
    
    scripts = ["wxvkmusic"],
    
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Sound/Audio :: Players"
    ],
    keywords="vk.com vk music player wx wxpython",
    cmdclass = CMD
)
