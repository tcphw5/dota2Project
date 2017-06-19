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
from bs4 import BeautifulSoup
import urllib.request
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lol@localhost/arcbase'
db = SQLAlchemy(app)

api = dota2api.Initialise("EECA0D811A31963E8E259DBB8EA055C4")


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





#Account IDs for manually found arc warden players
#MMRS: (vaxasmurf, 5k, 5k, 5k, 7k (alex the fool))
#can be changed for any hero later
#only one person for faster testing
#389202842, 131588917, 129705032, 128512494,
topPlayers = [11984011]
#hard coded for now
#hero_id = 113



@app.route('/')
def homepage():
    allHeros = api.get_heroes()['heroes']
    allHeros = sorted(allHeros, key=lambda x: x['localized_name'])
    return render_template("homepage.html", allHeros=allHeros)

@app.route('/result/<hero_id>', methods = ['POST', 'GET'])
def result(hero_id):
    if request.method == 'POST':
        allHeros = api.get_heroes()['heroes']
        topPlayers = dbuffScrape(hero_id, allHeros)
        result = countItems(topPlayers, hero_id)
        allItems = api.get_game_items()['items']
        result[0] = sorted(result[0].items(), key=lambda x: x[1], reverse=True)
        return render_template("result.html", result=result[0], total=result[1], allItems=allItems,
                               allHeros=allHeros, heroID=int(hero_id))

#returns a dict with total unique items and counts of purchaes in games played
#as <heroID> out of all <players> last 100 overall games
def countItems(players, heroID):

    allgames = []
    total_Items = []
    pictures = []
    match_counter = 0


    # goes though each players history and filters all the arc warden games into
    # the arcgames list.

    players = players[:2]
    #print(players)
    for player in players:
        #each call gets the last 100 TOTAL games (not just arc games)
        try:
            history = api.get_match_history(account_id=player)
            for game in history['matches']:
                for guy in game['players']:
                    if str(guy['account_id']) == str(player) and int(guy['hero_id']) == int(heroID):
                        allgames.append(game['match_id'])
        except Exception as e:
            continue


    # go through arc warden games one at a time counting items
    # saves new games to postgres database
    for gameID in allgames:
        match = api.get_match_details(match_id=gameID)
        print(match)
        for guy in match['players']:
            if int(guy['hero_id']) == int(heroID):
                match_counter += 1
                items = ["none", "none", "none", "none", "none", "none"]
                for x in range(6):
                    if guy['item_'+str(x)] != 0:
                        total_Items.append(guy['item_'+str(x)])

                #removed saving to db until ready
                #if Game3.query.filter_by(matchID=str(gameID)).first() is None:
                #    newgame = Game3(str(gameID), items[0], items[1], items[2], items[3], items[4], items[5])
                #   db.session.add(newgame)
                #    db.session.commit()

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


def dbuffScrape(hero_id, allHeros):

    dbuffHeroNames = {}
    for hero in allHeros:
        dbuffHeroNames.update({hero['id']: hero['localized_name'].lower().replace(" ", "-")})

    header = {'User-Agent': 'test header'}
    req = urllib.request.Request('https://www.dotabuff.com/heroes/' + dbuffHeroNames[int(hero_id)] + '/players',
                                 headers=header)
    page = None

    with urllib.request.urlopen(req) as response:
        page = response.read()

    soup = BeautifulSoup(page, "html.parser")

    table = soup.findChildren("table")

    topPlayers = table[1]

    rows = topPlayers.findChildren('tr')

    playerIDs = set()

    for row in rows:
        cells = row.findChildren('td')
        cells2 = row.findChildren('td')
        for cell in cells:
            if "segment-win" in (str(cell)):
                if float(cell.text[:-1]) < 80:
                    for cell2 in cells2:
                        for a in cell2.find_all('a', href=True):
                            if a['href'][:2] == "/p":
                                playerIDs.add(a['href'][9:])

    playerIDsList = list(playerIDs)
    playerIDsList = playerIDsList[1:]

    return playerIDsList

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
