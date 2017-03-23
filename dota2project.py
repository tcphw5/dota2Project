# -*- coding: utf-8 -*-
"""
tpwin10 created 2/3/2017

dota 2 project

"""

import dota2api

api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")

#match = api.get_match_details(match_id=2964787867)

#history = api.get_match_history(account_id=120732856)

#print(match)

#print(history)


#Account IDs for manually found arc warden players
#MMRS: (vaxasmurf, 5k, 5k, 5k, 7k (alex the fool))
players = [389202842, 131588917, 129705032, 128512494, 11984011]


for player in players:
    #each call gets the last 100 games
    history = api.get_match_history(account_id=player)
    for game in history['matches']:
        samplegame = game
    