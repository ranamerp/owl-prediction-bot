import json
import progressbar
import pandas as pd
import logging, sys
import pathlib
import grequests
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests as s

# Local Imports
from constants import MAP_TYPE, ID_TO_NAME, MATCH_COLUMS, GUID_TO_MAP_NAME, HERO_ROLES

#Dictionaries
DF_COLUMNS = ["id", "date", "stage", "away", "away id", "away score", "home", "home id", "home score", "winner", "winner id", "home point differential", "away point differential","winner label"]
match_colums = MATCH_COLUMS
MAP_COLUMNS = ["Name", "Type", "Away Points", "Home Points", "Winner"]


#Other Initializations
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='log.log')
logging.debug("Debug Activated")

#s = requests.Session()

#gets the entire OWL Schedule

def get_schedule(schedule, df, total, exists):
    currentnum = 0
    newflag = False
    if exists:
        #st = pd.read_csv(path)
        newflag = True

    with progressbar.ProgressBar(max_value=total) as bar:
        for i in schedule:
            #Ignoring All Stars as it has no impact on season standings
            if i["name"] == "All-Stars":
                continue
            for j in i["matches"]:
                id = j["id"]

                #check to see if data exists
                #figure out way to use DataFrame.update
                '''
                if newflag is False:
                    if id in st['id'].values:
                        if st[st.id == id].winner is not None:
                            currentnum += 1
                            bar.update(currentnum)
                            df.append(st[st.id == id], ignore_index=True)
                            continue
                '''

                date = j["startDate"]
                stage = j["bracket"]["stage"]["tournament"]["title"]
                away = j["competitors"][0]["name"]
                away_id = get_keys_by_value(away)
                away_score = j["scores"][0]["value"]
                home = j["competitors"][1]["name"]
                home_id = get_keys_by_value(home)
                home_score = j["scores"][1]["value"]

                #in the case that the match hasn't been played, winner will be NaN
                try:
                    winner = j["winner"]["name"]
                    if winner == home:
                        winner_label = "Home"
                        winner_id = home_id
                    if winner == away:
                        winner_label = "Away"
                        winner_id = away_id
                except KeyError:
                    winner = None
                    winner_id = None
                    continue

                #gets map data
                match_series = get_match_data(id, away, home)

                #adds all data to a series object
                dl = pd.Series([id, date, stage, away, away_id, away_score, home, home_id, home_score, winner, winner_id, home_score, away_score, winner_label], DF_COLUMNS)

                #merges map data with match data
                for k in match_series:
                    dl = pd.concat([dl, k])

                #general logging message
                logging.debug("%s vs %s recorded!", str(away), str(home))

                df = df.append(dl, ignore_index=True)

                #progress bar
                currentnum += 1
                bar.update(currentnum)



    return df

#gets the general map data
def get_match_data(id, away, home):
    #gets match id
    matches = s.get("https://api.overwatchleague.com/matches/{}".format(id))
    m = matches.json()
    match_series = []

    #get all map endpoints and call them at the same time
    numgame = len(m["games"])
    urls = []
    for i in range(1, numgame+1):
        urls.append("https://api.overwatchleague.com/stats/matches/{}/maps/{}".format(id, i))

    rs = (grequests.get(u) for u in urls)
    responses = grequests.map(rs)

    for i in m["games"]:

        number = i["number"]

        #if name is blank then both are None
        try:
            name = i["attributes"]["map"]
            if name is None:
                guid = i["attributes"]["mapGuid"]
                name = GUID_TO_MAP_NAME.get(guid)
            type = MAP_TYPE.get(name)
        except KeyError:
            name = None
            type = None

        #if map isn't played or data isn't recorded, both are none
        try:
            away_points = i["points"][0]
            home_points = i["points"][1]
        except:
            away_points = None
            home_points = None

        if away_points != None and home_points != None :
            if away_points > home_points:
                map_winner = "Away"
            elif away_points < home_points:
                map_winner = "Home"
            elif away_points == home_points:
                map_winner = "Draw"
        else:
            map_winner = None

        #iterates on colums so each index is unique
        colums = ["Map " + str(number) + " " + j for j in MAP_COLUMNS]

        #adds data to series
        map_numbers = pd.Series([name, type, away_points, home_points, map_winner], colums)

        #gets roster for each map
        roster_info = get_match_player(i, away, home, responses[number-1])

        #merges roster and map data
        map_data = pd.concat([map_numbers, roster_info[0], roster_info[1]])

        #appends to one series
        match_series.append(map_data)
    return match_series

#gets the roster fielded for each map
def get_match_player(m,away, home, r):
   #initialization of variables
    away_team_colums = ["Away Player 1", "Away Player 1 Elo", "Away Player 2", "Away Player 2 Elo", "Away Player 3", "Away Player 3 Elo",
                        "Away Player 4", "Away Player 4 Elo", "Away Player 5", "Away Player 5 Elo", "Away Player 6", "Away Player 6 Elo"]
    home_team_colums = ["Home Player 1", "Home Player 1 Elo", "Home Player 2", "Home Player 2 Elo", "Home Player 3", "Home Player 3 Elo",
                        "Home Player 4", "Home Player 4 Elo", "Home Player 5", "Home Player 5 Elo", "Home Player 6", "Home Player 6 Elo", ]
    home_team = []
    away_team = []

    #tests if map was anticipated to be played but was not played (This is primarily a 2018 artifact)
    if len(m["players"]) is 0:
        for i in range(0, 6):
            player_name = None
            away_team.append(player_name)
            home_team.append(player_name)

    #checks if response went through
    if r.status_code is not 200:
        st = None
    else:
        st = json.loads(r.content)

    for i in m["players"]:
        #gets player name and ID
        player_name = i['player']['name']
        player_id = i['player']["id"]

        #gets team name from ID
        team_id = i["team"]["id"]
        player_team = ID_TO_NAME.get(team_id)

        #calculate player impact score
        if st is None:
            elo = 0
        else:
            elo = get_player_elo(st, team_id, player_id)

        #sorts players into proper teams
        if player_team == away:
            away_team.append(player_name)
            away_team.append(elo)
        elif player_team == home:
            home_team.append(player_name)
            home_team.append(elo)

    # iterates on colums so each index is unique
    ht_colums = ["Map " + str(m['number']) + " " + j for j in home_team_colums]
    at_colums = ["Map " + str(m['number']) + " " + j for j in away_team_colums]

    #adds all data to series object
    ht= pd.Series(home_team, ht_colums)
    at= pd.Series(away_team, at_colums)
    return at, ht

def get_player_elo(st, teamID, playerID):
    #initialization of variables
    elo = 0
    damage = 0
    deaths = 0
    eliminations = 0
    healing = 0

    #gets stats from map for each player
    for i in st["teams"]:
        if i["esports_team_id"] == teamID:
            for j in i["players"]:
                if j["esports_player_id"] == playerID:
                    for k in j["stats"]:
                        if k["name"] == "damage":
                            damage = k["value"]
                        elif k["name"] == "deaths":
                            deaths = k["value"]
                        elif k["name"] == "eliminations":
                            eliminations = k["value"]
                        elif k["name"] == "healing":
                            healing = k["value"]
                        else:
                            continue
                    hero = j["heroes"][0]["name"]
                    role = HERO_ROLES.get(hero)
                    elo = calc_player_elo(role, damage, eliminations, healing, deaths)
                    break
    return elo

def calc_player_elo(role, damage, elims, healing, deaths):
    # Figure out how to make this work with api.py
    # get score before (from database. THIS SHOULD BE DONE IN MACHINE LEARNING NOTEBOOK)
    # calculate score based on stats
    # do an average score across all maps
    # compare to entire team

    # create a total team elo used to compare (for machine learning model)
    if role == "offense":
        damsc = (500 * (damage * 0.425)) / 2500
        esc = (500 * (elims * 0.275)) / 2500
        hsc = (500 * (healing * 0.075)) / 2500
        dsc = (500 * (deaths * 0.225)) / 2500
    elif role == "tank":
        damsc = (500 * (damage * 0.4)) / 2500
        esc = (500 * (elims * 0.2)) / 2500
        hsc = (500 * (healing * 0.3)) / 2500
        dsc = (500 * (deaths * 0.1)) / 2500
    elif role == "support":
        damsc = (500 * (damage * 0.125)) / 2500
        esc = (500 * (elims * 0.225)) / 2500
        hsc = (500 * (healing * 0.325)) / 2500
        dsc = (500 * (deaths * 0.325)) / 2500
    else:
        damsc = 0
        esc = 0
        hsc = 0
        dsc = 0

    elo = damsc + esc + hsc - dsc

    return elo


#gets data from api for each team and adds it to a list of dataframes
def get_data(df, exists):
    #TODO create a method that reads csv and creates a basic dataframe so it doesnt have to recollect data every time.

    schedule = s.get("https://api.overwatchleague.com/schedule?season={}".format(year))
    sd = schedule.json()

    #getting data
    numberofgames = get_size_of_schedule(sd)
    data = get_schedule(sd["data"]["stages"], df, numberofgames, exists)
    print("The {} Season was successfully collected".format(year))
    df.append(data)

    #merge both dataframes into one singular one in the case that multiple seasons are scraped
    #dataframes_con = pd.concat(dataframes, sort=False)

    return data

#created for progress bar
def get_size_of_schedule(sd):
    total = 0
    for i in sd["data"]["stages"]:
        if i["slug"] != 'all-star':
            total = total + len(i["matches"])
    return total


def get_keys_by_value(item):
    for key, value in ID_TO_NAME.items():
        if item == value:
            return key


if __name__ == "__main__":

    # create an empty dataframe
    owl_df = pd.DataFrame(columns=DF_COLUMNS + match_colums)

    #fill data
    year = input("Please enter the year you would like to collect (Note: any misinput will collect data from current year) : ")
    path = pathlib.Path('data{}.csv'.format(year))

    #check to see if database already exists
    if path.exists():
        exists = True
    else:
        exists = False

    owl_df = get_data(owl_df, exists)

    #sort values and delete duplicate data
    owl_df.sort_values("date", inplace = True)
    owl_df = owl_df.drop_duplicates("date", keep= 'last')



    #write to csv
    owl_df.to_csv('data{}.csv'.format(year), header=DF_COLUMNS + match_colums, index=False)









