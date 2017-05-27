# -*- coding: utf-8 -*-
"""
dota2 flask web app version

Created on Sat May 20 19:48:27 2017

@author: tpwin10
"""
# Flask stuff
from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
#arc track stuff
import dota2api
from collections import Counter
import pandas as pd
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lol@localhost/arcbase'
db = SQLAlchemy(app)


# set up db object for stored games
class Game3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matchID = db.Column(db.String(80), unique=True)
    item1 = db.Column(db.String(80), unique=False)
    item2 = db.Column(db.String(80), unique=False)
    item3 = db.Column(db.String(80), unique=False)
    item4 = db.Column(db.String(80), unique=False)
    item5 = db.Column(db.String(80), unique=False)
    item6 = db.Column(db.String(80), unique=False)

    def __init__(self, matchID, item1, item2, item3, item4, item5, item6):
        self.matchID = matchID
        self.item1 = item1
        self.item2 = item2
        self.item3 = item3
        self.item4 = item4
        self.item5 = item5
        self.item6 = item6

    def __repr__(self):
        return '<MatchID %r' & self.matchID



api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")

#Account IDs for manually found arc warden players
#MMRS: (vaxasmurf, 5k, 5k, 5k, 7k (alex the fool))
#can be changed for any hero later
#only one person for faster testing
#389202842, 131588917, 129705032, 128512494,
arcPlayers = players = [11984011]
#hard coded for now
arc_id = 113



@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'GET':
        #counting items with hardcoded arc things (obviously. "arc" tracker atm)
        result = countItems(arcPlayers, arc_id)
        result[0] = sorted(result[0].items(), key=lambda x: x[1], reverse=True)
        return render_template("result.html", result = result[0], total = result[1])

#returns a dict with total unique items and counts of purchaes in games played
#as <heroID> out of all <players> last 100 overall games
def countItems(players, heroID):
    games = []

    allItems = api.get_game_items()['items']
    total_Items = []
    match_counter = 0


    # goes though each players history and filters all the arc warden games into
    # the arcgames list.
    for player in players:
        #each call gets the last 100 TOTAL games (not just arc games)
        try:
            history = api.get_match_history(account_id=player)
            for game in history['matches']:
                for guy in game['players']:
                    if guy['account_id'] == player and guy['hero_id'] == heroID:
                        games.append(game['match_id'])
        except Exception as e:
            continue


    # go through arc warden games one at a time counting items
    # saves new games to postgres database
    for gameID in games:
        match = api.get_match_details(match_id=gameID)
        for guy in match['players']:
            if guy['hero_id'] == heroID:
                match_counter += 1
                items = ["none", "none", "none", "none", "none", "none"]
                for x in range(6):
                    if guy['item_'+str(x)] != 0:
                        total_Items.append(guy['item_'+str(x)+'_name'])
                        items[x] = guy['item_'+str(x)+'_name']
                if Game3.query.filter_by(matchID=str(gameID)).first() is None:
                    newgame = Game3(str(gameID), items[0], items[1], items[2], items[3], items[4], items[5])
                    db.session.add(newgame)
                    db.session.commit()

                '''
                #backpack not counted for now
                for x in range(3):
                    total_arc_Items.append(guy['backpack_'+str(x)])
                '''
    total_Items = [x for x in total_Items if x != 0]
    countedItems = Counter(total_Items)
    countedItemsDict = dict(countedItems)
    results = []
    results.append(countedItemsDict)
    results.append(match_counter)
    return results


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
