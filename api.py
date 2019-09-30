import requests
import json

import pandas as pd
import logging, sys
import os

# Local Imports
from constants import MAP_TYPE, ID_TO_NAME, MATCH_COLUMS

#API Requests
schedule = requests.get("https://api.overwatchleague.com/schedule")
schedule_2018 = requests.get("https://api.overwatchleague.com/schedule?season=2018")

#Dictionaries
DF_COLUMNS = ["date", "stage", "away", "away score", "home", "home score","winner"]
match_colums = MATCH_COLUMS
MAP_COLUMNS = ["Name", "Type", "Away Points", "Home Points"]

#JSON Loading of API Repsonses
sd = json.loads(schedule.text)
sd18 = json.loads(schedule_2018.text)

#Other Initializations
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug("Debug Activated")


#gets the entire OWL Schedule
def get_schedule(schedule, df):
    for i in schedule:
        if i["name"] == "All-Stars":
            continue
        for j in i["matches"]:
            if j['conclusionStrategy'] == "BEST_OF" or j['conclusionStrategy'] == "FIRST_TO":
                continue
            id = j["id"]
            date = j["startDate"]
            stage = j["bracket"]["stage"]["tournament"]["title"]
            away = j["competitors"][0]["name"]
            away_score = j["scores"][0]["value"]
            home = j["competitors"][1]["name"]
            home_score = j["scores"][1]["value"]
            try:
                winner = j["winner"]["name"]
            except KeyError:
                winner = "N/A"
                continue
            match_series = get_match_data(id, away, home)
            dl = pd.Series([date, stage, away, away_score, home, home_score, winner], DF_COLUMNS)
            for k in match_series:
                dl = pd.concat([dl, k])
            logging.debug("%s vs %s recorded!", str(away), str(home))
            df = df.append(dl, ignore_index=True)



    return df

def get_match_data(id, away, home):
    matches = requests.get("https://api.overwatchleague.com/matches/{}".format(id))
    m = json.loads(matches.text)
    match_series = []
    for i in m["games"]:
        number = i["number"]
        try:
            name = i["attributes"]["map"]
            type = MAP_TYPE.get(name)
        except KeyError:
            name = None
            type = None
        try:
            away_points = i["points"][0]
            home_points = i["points"][1]
        except:
            away_points = None
            home_points = None
        colums = ["Map " + str(number) + " " + j for j in MAP_COLUMNS]
        map_numbers = pd.Series([name, type, away_points, home_points], colums)
        roster_info = get_match_player(i, away, home)
        map_data = pd.concat([map_numbers, roster_info[0], roster_info[1]])
        match_series.append(map_data)
    return match_series

def get_match_player(m,away,home):
    away_team_colums = ["Away Player 1", "Away Player 2", "Away Player 3", "Away Player 4", "Away Player 5", "Away Player 6"]
    home_team_colums = ["Home Player 1", "Home Player 2", "Home Player 3", "Home Player 4", "Home Player 5", "Home Player 6"]
    home_team = []
    away_team = []
    for i in m["players"]:
        player_name = i['player']['name']
        team_id = i["team"]["id"]
        player_team = ID_TO_NAME.get(team_id)
        if player_team == away:
            away_team.append(player_name)
        elif player_team == home:
            home_team.append(player_name)
    ht_colums = ["Map " + str(m['number']) + " " + j for j in home_team_colums]
    at_colums = ["Map " + str(m['number']) + " " + j for j in away_team_colums]
    ht= pd.Series(home_team, ht_colums)
    at= pd.Series(away_team, at_colums)
    return at, ht

#gets data from api for each team and adds it to a list of dataframes
def get_data(df):
    dataframes = []
    data2018 = get_schedule(sd18["data"]["stages"], df)
    dataframes.append(data2018)
    print("The 2018 Season was successfully collected")
    data2019 = get_schedule(sd["data"]["stages"], df)
    dataframes.append(data2019)
    print("The 2019 Season was successfully collected")
    dataframes_con = pd.concat(dataframes, sort=False)

    return dataframes_con


if __name__ == "__main__":

    # create an empty dataframe
    owl_df = pd.DataFrame(columns=DF_COLUMNS + match_colums)


    #fill data
    owl_df = get_data(owl_df)

    #sort values and delete duplicate data
    owl_df.sort_values("date", inplace = True)
    owl_df = owl_df.drop_duplicates("date")



    #write to csv
    owl_df.to_csv('data.csv', header=DF_COLUMNS + match_colums, index=False)








