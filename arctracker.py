# -*- coding: utf-8 -*-
"""
dota2 flask web app version

Created on Sat May 20 19:48:27 2017

@author: tpwin10
"""
#Flask stuff
from flask import Flask, render_template, request
app = Flask(__name__)
#

#arc track stuff
import dota2api
from collections import Counter
import pandas as pd

api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")

#Account IDs for manually found arc warden players
#MMRS: (vaxasmurf, 5k, 5k, 5k, 7k (alex the fool))
#can be changed for any hero later
arcPlayers =    players = [389202842, 131588917, 129705032, 128512494, 11984011]
#hard coded for now
arc_id = 113
#

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'GET':
        #counting items with hardcoded arc things (obviously. "arc" tracker atm)
        result = countItems(arcPlayers, arc_id)
        return render_template("result.html", result = result)

#returns a dict with total unique items and counts of purchaes in games played
#as <heroID> out of all <players> last 100 overall games
def countItems(players, heroID):
    games = []

    allItems = api.get_game_items()['items']
    total_Items = []
    match_counter = 0


    #goes though each players history and filters all the arc warden games into
    #the arcgames list.
    for player in players:
        #each call gets the last 100 games
        try:
            history = api.get_match_history(account_id=player)
            for game in history['matches']:
                for guy in game['players']:
                    if guy['account_id'] == player and guy['hero_id'] == heroID:
                        games.append(game['match_id'])
        except Exception as e:
            continue


    #go through arc warden games one at a time counting items
    for gameID in games:
        match = api.get_match_details(match_id=gameID)
        for guy in match['players']:
            if guy['hero_id'] == heroID:
                match_counter += 1
                for x in range(5):
                    if guy['item_'+str(x+1)] != 0:
                        total_Items.append(guy['item_'+str(x+1)+'_name'])
                '''
                #backpack not counted for now
                for x in range(3):
                    total_arc_Items.append(guy['backpack_'+str(x)])
                '''
    total_Items = [x for x in total_Items if x != 0]
    countedItems = Counter(total_Items)
    countedItemsDict = dict(countedItems)

    return countedItemsDict


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
