import requests
import json

import pandas as pd
import os

# Local Imports
from constants import MAP_TYPE

#API Requests
schedule = requests.get("https://api.overwatchleague.com/schedule")
schedule_2018 = requests.get("https://api.overwatchleague.com/schedule?season=2018")

#Dictionaries (May move to constants)
team_id = [7698, 4402, 7692, 4523, 4407, 7699, 7693, 4525, 4410, 4406, 4405, 4403, 7694, 4524, 4404, 4409, 4408, 7695, 7696, 7697]
DF_COLUMNS = ["date", "away", "away score", "home", "home score","winner"]
MATCH_COLUMS = ["Map 1 Name", "Map 1 Type", "Map 1 Away Points", "Map 1 Home Points",
                "Map 2 Name", "Map 2 Type", "Map 2 Away Points", "Map 2 Home Points",
                "Map 3 Name", "Map 3 Type", "Map 3 Away Points", "Map 3 Home Points",
                "Map 4 Name", "Map 4 Type", "Map 4 Away Points", "Map 4 Home Points",
                "Map 5 Name", "Map 5 Type", "Map 5 Away Points", "Map 5 Home Points"]

#JSON Loading of API Repsonses
sd = json.loads(schedule.text)
sd18 = json.loads(schedule_2018.text)



#gets the entire OWL Schedule
def get_schedule(schedule, df):
    for i in schedule:
        if i["name"] == "All-Stars":
            continue
        for j in i["matches"]:
            if j['conclusionStrategy'] == "BEST_OF":
                continue
            date = j["startDate"]
            away = j["competitors"][0]["name"]
            away_score = j["scores"][0]["value"]
            home = j["competitors"][1]["name"]
            home_score = j["scores"][1]["value"]
            try:
                winner = j["winner"]["name"]
            except KeyError:
                winner = "N/A"
                continue
            match_series = get_match_data(j)
            dl = pd.Series([date, away, away_score, home, home_score, winner], DF_COLUMNS)
            d2 = pd.concat([dl, match_series])
            df = df.append(d2, ignore_index=True)

    return df
def get_match_data(m):
    try:
        map_1_name = m["games"][0]["attributes"]["map"]
    except KeyError:
        map_1_name = "None"
    map_1_type = MAP_TYPE.get(map_1_name)
    map_1_away_points = m["games"][0]["points"][0]
    map_1_home_points = m["games"][0]["points"][1]

    try:
        map_2_name = m["games"][1]["attributes"]["map"]
    except KeyError:
        map_2_name = "None"
    map_2_type = MAP_TYPE.get(map_2_name)
    map_2_away_points = m["games"][1]["points"][0]
    map_2_home_points = m["games"][1]["points"][1]

    try:
        map_3_name = m["games"][2]["attributes"]["map"]
    except KeyError:
        map_3_name = "None"
    map_3_type = MAP_TYPE.get(map_3_name)
    map_3_away_points = m["games"][2]["points"][0]
    map_3_home_points = m["games"][2]["points"][1]

    try:
        map_4_name = m["games"][3]["attributes"]["map"]
    except KeyError:
        map_4_name = "None"
    map_4_type = MAP_TYPE.get(map_4_name)
    map_4_away_points = m["games"][3]["points"][0]
    map_4_home_points = m["games"][3]["points"][1]

    try:
        map_5_name = m["games"][4]["attributes"]["map"]
        map_5_type = MAP_TYPE.get(map_5_name)
        map_5_away_points = m["games"][4]["points"][0]
        map_5_home_points = m["games"][4]["points"][1]
    except (IndexError, KeyError) as e:
        map_5_name = "N/A"
        map_5_type = "N/A"
        map_5_away_points = "N/A"
        map_5_home_points = "N/A"
    series = pd.Series([map_1_name, map_1_type, map_1_away_points, map_1_home_points,
                        map_2_name, map_2_type, map_2_away_points, map_2_home_points,
                        map_3_name, map_3_type, map_3_away_points, map_3_home_points,
                        map_4_name, map_4_type, map_4_away_points, map_4_home_points,
                        map_5_name, map_5_type, map_5_away_points, map_5_home_points], MATCH_COLUMS)
    return series



#gets data from api for each team and adds it to a list of dataframes
def get_data(df):
    dataframes = []
    data2018 = get_schedule(sd18["data"]["stages"], df)
    dataframes.append(data2018)
    data2019 = get_schedule(sd["data"]["stages"], df)
    dataframes.append(data2019)
    dataframes_con = pd.concat(dataframes)

    return dataframes_con


if __name__ == "__main__":

    # create an empty dataframe
    owl_df = pd.DataFrame(columns=DF_COLUMNS)

    #fill data
    owl_df = get_data(owl_df)

    #sort values and delete duplicate data
    owl_df.sort_values("date", inplace = True)
    owl_df = owl_df.drop_duplicates("date")



    #write to csv
    owl_df.to_csv('data.csv', header=DF_COLUMNS + MATCH_COLUMS, index=False)








