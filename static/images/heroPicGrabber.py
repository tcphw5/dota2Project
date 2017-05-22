# -*- coding: utf-8 -*-
"""
Created on Mon May 22 00:55:19 2017

@author: tpwin10
"""
import dota2api
import urllib.request
api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")

allHeros = api.get_heroes()

for hero in allHeros['heroes']:
    urllib.request.urlretrieve(hero['url_full_portrait'], hero['name'] + ".png")

