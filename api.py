import requests
import json
import time
import progressbar
import pandas as pd
import logging, sys
import os

# Local Imports
from constants import MAP_TYPE, ID_TO_NAME, MATCH_COLUMS, GUID_TO_MAP_NAME

#Dictionaries
DF_COLUMNS = ["date", "stage", "away", "away id", "away score", "home", "home id", "home score", "winner", "winner id", "home point differential", "away point differential","winner label"]
match_colums = MATCH_COLUMS
MAP_COLUMNS = ["Name", "Type", "Away Points", "Home Points", "Winner"]


#Other Initializations
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='log.log')
logging.debug("Debug Activated")



#gets the entire OWL Schedule

def get_schedule(schedule, df, total):
    currentnum = 0
    with progressbar.ProgressBar(max_value=total) as bar:
        for i in schedule:
            #Ignoring All Stars as it has no impact on season standings
            if i["name"] == "All-Stars":
                continue
            for j in i["matches"]:
                id = j["id"]
                date = j["startDate"]
                stage = j["bracket"]["stage"]["tournament"]["title"]
                away = j["competitors"][0]["name"]
                away_id = get_keys_by_value(away)
                away_score = j["scores"][0]["value"]
                home = j["competitors"][1]["name"]
                home_id = get_keys_by_value(home)
                home_score = j["scores"][1]["value"]
                home_dif = home_score - away_score
                away_dif = away_score - home_score

                #in the case that the match hasn't been played, winner will be NaN
                try:
                    winner = j["winner"]["name"]
                    winner_id = get_keys_by_value(winner)
                    if winner == home:
                        winner_label = "Home"
                    if winner == away:
                        winner_label = "Away"
                except KeyError:
                    winner = None
                    winner_id = None
                    continue
                #gets map data
                match_series = get_match_data(id, away, home)

                #adds all data to a series object
                dl = pd.Series([date, stage, away, away_id, away_score, home, home_id, home_score, winner, winner_id, home_score, away_score, winner_label], DF_COLUMNS)

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
    matches = requests.get("https://api.overwatchleague.com/matches/{}".format(id))
    m = json.loads(matches.text)
    match_series = []

    for i in m["games"]:

        number = i["number"]
        #if name is blank then both are None
        try:
            guid = i["attributes"]["mapGuid"]
            name = i["attributes"]["map"] or GUID_TO_MAP_NAME.get(guid)
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
        roster_info = get_match_player(i, away, home)

        #merges roster and map data
        map_data = pd.concat([map_numbers, roster_info[0], roster_info[1]])

        #appends to one series
        match_series.append(map_data)
    return match_series

#gets the roster fielded for each map
def get_match_player(m,away,home):
    # TODO Create method that gets heroes used by each player.
    #initialization of variables
    away_team_colums = ["Away Player 1", "Away Player 2", "Away Player 3", "Away Player 4", "Away Player 5", "Away Player 6"]
    home_team_colums = ["Home Player 1", "Home Player 2", "Home Player 3", "Home Player 4", "Home Player 5", "Home Player 6"]
    home_team = []
    away_team = []

    #tests if map was anticipated to be played but was not played (This is primarily a 2018 artifact)
    if len(m["players"]) is 0:
        for i in range(0, 6):
            player_name = None
            away_team.append(player_name)
            home_team.append(player_name)

    for i in m["players"]:
        player_name = i['player']['name']

        #gets team name from ID
        team_id = i["team"]["id"]
        player_team = ID_TO_NAME.get(team_id)

        #sorts players into proper teams
        if player_team == away:
            away_team.append(player_name)
        elif player_team == home:
            home_team.append(player_name)

    # iterates on colums so each index is unique
    ht_colums = ["Map " + str(m['number']) + " " + j for j in home_team_colums]
    at_colums = ["Map " + str(m['number']) + " " + j for j in away_team_colums]

    #adds all data to series object
    ht= pd.Series(home_team, ht_colums)
    at= pd.Series(away_team, at_colums)
    return at, ht



#gets data from api for each team and adds it to a list of dataframes
def get_data(df):
    #TODO create a method that reads csv and creates a basic dataframe so it doesnt have to recollect data every time.
    #dataframes = []



    '''
    #starting with 2018
    numberofgames = get_size_of_schedule(sd18)
    data2018 = get_schedule(sd18["data"]["stages"], df, numberofgames)
    dataframes.append(data2018)
    print("The 2018 Season was successfully collected")
    '''
    schedule = requests.get("https://api.overwatchleague.com/schedule?season={}".format(year))
    sd = json.loads(schedule.text)

    #continuing to 2019
    numberofgames = get_size_of_schedule(sd)
    data = get_schedule(sd["data"]["stages"], df, numberofgames)
    print("The {} Season was successfully collected".format(year))
    df.append(data)

    #merge both dataframes into one singular one
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
    owl_df = get_data(owl_df)

    #sort values and delete duplicate data
    owl_df.sort_values("date", inplace = True)
    owl_df = owl_df.drop_duplicates("date")



    #write to csv
    owl_df.to_csv('data{}.csv'.format(year), header=DF_COLUMNS + match_colums, index=False)








