#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
# wx VK Music 
# Free & OpenSource music player for vk.com social network
# https://bitbucket.org/xxblx/wx-vk-music
# 
# Oleg Kozlov (xxblx), 2014 - 2015
###########################################################

import vk
from time import sleep
from requests.exceptions import ConnectionError, HTTPError
from random import randint

vkapi = None
                
def login_to_vk(login, pwd):
    """ Login to vk.com """
    
    try:
        vkapi = vk.API("4649463", login, pwd, scope="audio")
        vkapi("stats.trackVisitor")
        return True, vkapi
    # If Error return False and error description
    except vk.api.VkAuthorizationError:
        return False, "Bad login or password"
    except ConnectionError:
        return False, "Connection problem"
    except:
        return False, "Unknown problem"

def get_access(token):
    """ Get access to vk.com by access_token """
    
    try:
        vkapi = vk.API(access_token=token)
        vkapi("stats.trackVisitor")
        return True, vkapi
    except vk.api.VkAuthorizationError:
        return False, "Bad access token"
    except ConnectionError:
        return False, "Connection problem"
    except:
        return False, "Unknown problem"

def convert_id_name(i):
    """ Convert screen name to ID """
    
    if i[0] == "-":
        i = -vkapi("groups.getById", group_ids=i[1:])[0][u"id"]
    else:
        i = vkapi("users.get", user_ids=i)[0][u"id"]
        
    return i

def get_audios_list(i, album, tm=5):
    """ Get list from vk.com with audiotracks """
    
    if album:
        audios = vkapi("audio.get", owner_id=i, album_id=album, 
                       timeout=tm, count=6000)
    else:
        audios = vkapi("audio.get", owner_id=i, timeout=tm, count=6000)
        
    return audios

def get_audios(i, album=False):
    """ Get audios list """
    
    # If too many requests per second need to set delay
    try:
        i = convert_id_name(i)
    except vk.api.VkAPIMethodError as e:
        if e.code == 6:
            sleep(0.5)
            i = convert_id_name(i)

    try:
        return get_audios_list(i, album)
    # If playlist has 2500+ audiotracks need to set "big" timeout
    except HTTPError:
        sleep(1)
        return get_audios_list(i, album, tm=30)
    except vk.api.VkAPIMethodError:
        return False

def get_rand_i(l):
    """ Get random int from (0, l) """
    
    return randint(0, l)

def search_audios(q, po, so, ac, tm=5):
    """ 
    Search audios on vk.com
    q - search query
    po - perfomer_only
    so - search_own
    ac - auto_complete    
    """    
    
    try:
        return vkapi("audio.search", q=q, performer_only=po, sort=2, offset=0,
                     count=300, search_own=so, auto_complete=ac, timeout=tm)
    except vk.api.VkAPIMethodError:
        return False
