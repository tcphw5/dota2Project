# -*- coding: utf-8 -*-
"""
tpwin10 created 2/3/2017

dota 2 project

"""

import dota2api
from collections import Counter
import pandas as pd

api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")

#match = api.get_match_details(match_id=2964787867)

#history = api.get_match_history(account_id=120732856)

#print(match)

#print(history)

fileOUT = open('Output.txt', 'w', encoding='utf-8')


#Account IDs for manually found arc warden players
#MMRS: (vaxasmurf, 5k, 5k, 5k, 7k (alex the fool))
players = [389202842, 131588917, 129705032, 128512494, 11984011]

#can be changed for any hero later
arcgames = []
#hard coded for now
arc_id = 113

allItems = api.get_game_items()['items']
total_arc_Items = []
match_counter = 0


#goes though each players history and filters all the arc warden games into
#the arcgames list.
for player in players:
    #each call gets the last 100 games
    history = api.get_match_history(account_id=player)
    for game in history['matches']:
        for guy in game['players']:
            if guy['account_id'] == player and guy['hero_id'] == arc_id:
                arcgames.append(game['match_id'])
        
#go through arc warden games one at a time counting items
for gameID in arcgames:
    match = api.get_match_details(match_id=gameID)
    for guy in match['players']:
        if guy['hero_id'] == arc_id:
            match_counter += 1
            for x in range(5):
                if guy['item_'+str(x+1)] != 0:
                    total_arc_Items.append(guy['item_'+str(x+1)+'_name'])
            '''
            #backpack not counted for now
            for x in range(3):
                total_arc_Items.append(guy['backpack_'+str(x)])
            '''    
total_arc_Items = [x for x in total_arc_Items if x != 0]
countedArcItems = Counter(total_arc_Items)
countedArcItemsDict = dict(countedArcItems)
fileOUT.write(str(len(countedArcItemsDict.keys())) + ' different items purchased across ' + str(match_counter) + ' games.\n\n')
fileOUT.write(str(countedArcItemsDict))

df = pd.DataFrame.from_dict(countedArcItems, orient='index')
df.plot(kind='bar')

fileOUT.close()