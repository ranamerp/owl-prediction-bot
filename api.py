import requests
import json

import pandas as pd
import os

# Initalization/ Global Variables
schedule = requests.get("https://api.overwatchleague.com/schedule")
team_id = [7698, 4402, 7692, 4523, 4407, 7699, 7693, 4525, 4410, 4406, 4405, 4403, 7694, 4524, 4404, 4409, 4408, 7695, 7696, 7697]
DF_COLUMNS = ["date", "away", "away score", "home", "home score", "winner"]
sd = json.loads(schedule.text)



#gets the entire OWL Schedule
def get_schedule(team, df):
    for i in team:
        date = get_date_played(i["id"])
        away = i["competitors"][0]["name"]
        away_score = i["scores"][0]["value"]
        home = i["competitors"][1]["name"]
        home_score = i["scores"][1]["value"]
        try:
            winner = i["winner"]["name"]
        except KeyError:
            winner = "N/A"
        dl = pd.Series([date, away, away_score, home, home_score, winner], DF_COLUMNS)
        df = df.append(dl, ignore_index=True)

    return df

#gets the specific day played for a match
def get_date_played(id):
    found = False
    while not found:
        for i in sd["data"]["stages"]:
            for j in i["matches"]:
                if j["id"] == id:
                    date = j["startDate"]
                    found = True
                    break
            if found:
                break
        if found:
            break

    return date

#gets data from api for each team and adds it to a list of dataframes
def get_data(df):
    dataframes = []
    for i in team_id:
        current_team = i
        team = requests.get("https://api.overwatchleague.com/teams/{}".format(current_team))
        tt = json.loads(team.text)
        data = get_schedule(tt["schedule"], df)
        dataframes.append(data)

    return dataframes


if __name__ == "__main__":

    # create an empty dataframe
    owl_df = pd.DataFrame(columns=DF_COLUMNS)

    #fill data
    owl_df = get_data(owl_df)

    #write to csv
    i = 0
    #takes dataframes from list and writes to csv
    while i < len(owl_df):
        if not os.path.isfile('data.csv'):
           owl_df[i].to_csv('data.csv', header=DF_COLUMNS, index=False)
        else:
            owl_df[i].to_csv('data.csv', mode='a', header=False, index=False)
        i+=1








