
#imports
import pandas as pd
import numpy as np
import itertools
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale

from random import randrange
from constants import ID_TO_NAME
NAME_TO_ID = {y:x for x,y in ID_TO_NAME.items()}

def data_processing(df, stats):

    # filtering out the data
    colums = ["winning_team", "winner_score", "losing_team", "loser_score",
              "map_1_name", "map_1_type", "map_1_winner", "map_1_winner_score", "map_1_loser_score", "map_1_loser",
              "map_2_name", "map_2_type", "map_2_winner", "map_2_winner_score", "map_2_loser_score", "map_2_loser",
              "map_3_name", "map_3_type", "map_3_winner", "map_3_winner_score", "map_3_loser_score", "map_3_loser",
              "map_4_name", "map_4_type", "map_4_winner", "map_4_winner_score", "map_4_loser_score", "map_4_loser",
              "map_5_name", "map_5_type", "map_5_winner", "map_5_winner_score", "map_5_loser_score", "map_5_loser"]

    filtered_df = df[colums]

    cols = ["Points Earned", "Points Lost", "Points Differential", "Points Differential Rank", "True Win %",
            "Map Potential %", "Map Potential % Rank"]
    types = ["Average Assault", "Average Control", "Average Hybrid", "Average Escort"]
    columns = []
    for i in types:
        columns.append([i + " " + j for j in cols])

    columns = list(itertools.chain.from_iterable(columns))

    sta = stats[columns]

    cols = ["Wins", "Losses", "Draws"]
    types = ["Total Assault", "Total Control", "Total Hybrid", "Total Escort"]
    columns.clear()
    for i in types:
        columns.append([i + " " + j for j in cols])
    columns = list(itertools.chain.from_iterable(columns))
    sta2 = stats[columns]

    filtered_stats = pd.concat([sta2, sta], axis=1)

    finaldf = []
    filtered_df = filtered_df[["winning_team", "winner_score", "losing_team", "loser_score"]]

    for index, row in filtered_df.iterrows():
        rannum = randrange(2)
        if rannum == 0:
            row["team1"] = NAME_TO_ID.get(row["winning_team"])
            row["team2"] = NAME_TO_ID.get(row["losing_team"])
            team1 = row["winning_team"]
            team2 = row["losing_team"]
        else:
            row["team1"] = NAME_TO_ID.get(row["losing_team"])
            row["team2"] = NAME_TO_ID.get(row["winning_team"])
            team2 = row["winning_team"]
            team1 = row["losing_team"]
        winnerrow = get_team_stats(team1, filtered_stats)
        loserrow = get_team_stats(team2, filtered_stats)
        winnerrow = winnerrow.rename(lambda x: "team1_" + x)
        loserrow = loserrow.rename(lambda x: "team2_" + x)
        test = pd.concat([row, winnerrow, loserrow], )
        finaldf.append(test)
    finaldf = pd.DataFrame(finaldf)
    finaldf.insert(finaldf.columns.get_loc("team2") + 1, 'Team1Win', finaldf.apply(home_team_winner, axis=1))

    # dropping all catagorical data
    finaldf = finaldf.drop(["winning_team", "winner_score", "losing_team", "loser_score"], axis=1)
    finaldf = finaldf.loc[:, ~finaldf.columns.str.contains("Rank")]

    return finaldf



def get_team_stats(team, stats):
    teamrow = stats.loc[team, :]
    return teamrow

def home_team_winner(row):
    if row['team1'] == NAME_TO_ID.get(row['winning_team']):
        return 1
    else:
        return 0

def initmodel(data, stats, filters):
    processed = data_processing(data, stats)

    df = processed

    # setting all data to same scale
    X = df.loc[:, ~df.columns.isin(['Team1Win'])]
    y = df.loc[:, 'Team1Win']

    for col in X.loc[:, "team1_Total Assault Wins": "team2_Average Escort Map Potential %"].columns:
        X[col] = scale(X[col])

    # splitting into training and testing
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.6,
                                                        stratify= df.loc[:, "Team1Win"],
                                                        random_state=69)

    rfc = RandomForestClassifier(500, random_state=534)
    rfc.fit(X_train, y_train)
    print('-- Random Forest -- ')
    print_results(X_train, X_test, y_train, y_test, df, rfc)
    with open('models/randomforest.pkl', 'wb') as f:
        pickle.dump([rfc, filters, stats], f)

    lr = LogisticRegression(random_state=534)
    lr.fit(X_train, y_train)
    print('-- Logistic Regression -- ')
    print_results(X_train, X_test, y_train, y_test, df, lr)
    with open('models/logisticregression.pkl', 'wb') as f:
        pickle.dump([lr, filters, stats], f)

    knn = KNeighborsClassifier()
    knn.fit(X_train, y_train)
    print('-- K Nearest Neighbors -- ')
    print_results(X_train, X_test, y_train, y_test, df, knn)
    with open('models/kneighbors.pkl', 'wb') as f:
        pickle.dump([knn, filters, stats], f)


    sv = SVC()
    sv.fit(X_train, y_train)
    print('-- SVC -- ')
    print_results(X_train, X_test, y_train, y_test, df, sv)
    with open('models/svc.pkl', 'wb') as f:
        pickle.dump([sv, filters, stats], f)


def print_results(X_train, X_test, y_train, y_test, df, model):
    print('Training Accuracy: ', accuracy_score(y_train, model.predict(X_train)))
    print('Testing Accuracy: ', accuracy_score(y_test, model.predict(X_test)))
    print('Whole Dataset: ', accuracy_score(df['Team1Win'], model.predict(df.loc[:, X_train.columns])))
    print('\n')



def get_model(model):
    model = "models/" + model
    with open(model, 'rb') as f:
        modl, filters = pickle.load(f)
    return modl, filters

