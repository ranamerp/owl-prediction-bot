import requests
import json

import pandas as pd
import os

# Initalization/ Global Variables
schedule = requests.get("https://api.overwatchleague.com/schedule")
schedule_2018 = requests.get("https://api.overwatchleague.com/schedule?season=2018")
team_id = [7698, 4402, 7692, 4523, 4407, 7699, 7693, 4525, 4410, 4406, 4405, 4403, 7694, 4524, 4404, 4409, 4408, 7695, 7696, 7697]
DF_COLUMNS = ["date", "away", "away score", "home", "home score","winner"]
sd = json.loads(schedule.text)
sd18 = json.loads(schedule_2018.text)



#gets the entire OWL Schedule
def get_schedule(schedule, df):
    for i in schedule:
        if i["name"] == "All-Stars":
            continue
        for j in i["matches"]:
            date = j["startDate"]
            away = j["competitors"][0]["name"]
            away_score = j["scores"][0]["value"]
            home = j["competitors"][1]["name"]
            home_score = j["scores"][1]["value"]
            try:
                winner = j["winner"]["name"]
            except KeyError:
                winner = "N/A"
            dl = pd.Series([date, away, away_score, home, home_score, winner], DF_COLUMNS)
            df = df.append(dl, ignore_index=True)

    return df
def get_match_data(id):
    match_data = []
    matches = requests.get("https://api.overwatchleague.com/matches/{}".format(id))
    m = json.loads(matches.text)
    map_1_name = m["games"][0]["attributes"]["map"]
    map_1_away_points = m["games"][0]["points"][0]
    map_1_home_points = m["games"][0]["points"][1]
    map_2_name = m["games"][1]["attributes"]["map"]
    map_2_away_points = m["games"][1]["points"][0]
    map_2_home_points = m["games"][1]["points"][1]
    map_3_name = m["games"][2]["attributes"]["map"]
    map_3_away_points = m["games"][2]["points"][0]
    map_3_home_points = m["games"][2]["points"][1]
    map_4_name = m["games"][3]["attributes"]["map"]
    map_4_away_points = m["games"][3]["points"][0]
    map_4_home_points = m["games"][3]["points"][1]
    try:
        map_5_name = m["games"][4]["attributes"]["map"]
        map_5_away_points = m["games"][4]["points"][0]
        map_5_home_points = m["games"][4]["points"][1]
    except IndexError:
        pass







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
    owl_df.to_csv('data.csv', header=DF_COLUMNS, index=False)








