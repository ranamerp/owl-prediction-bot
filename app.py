import numpy as np
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
import pickle
import os
import itertools


import datacollection
import machinelearning
from constants import ID_TO_NAME
NAME_TO_ID = {y:x for x,y in ID_TO_NAME.items()}


app = Flask(__name__)
app.secret_key = 'T5lzwP5cIfvJMoopGRTxUw'


@app.route('/')
def home():
    if request.method == "GET":
        for filename in os.listdir("models"):
            if "kneighbor" in filename:
                knn = get_model(filename)
                knnfilters = knn[1]
            elif "logistic" in filename:
                log = get_model(filename)
                logfilters = log[1]
            elif "random" in filename:
                random = get_model(filename)
                randomfilters = random[1]
            elif "svc" in filename:
                svc = get_model(filename)
                svcfilters = svc[1]
            else:
                pass

        return render_template('index.html',
                               knnfilters=knnfilters,
                               logfilters=logfilters,
                               randomfilters=randomfilters,
                               svcfilters=svcfilters)
    return render_template('index.html')
@app.route('/choice', methods = ["GET", "POST"])
def choice():
    decision = 'index.html'

    if request.method == "POST":
        form = request.form.getlist("choice")
        if form[0] == "yes":
            decision = "filters.html"
        elif form[0] == "no":
            decision = "model.html"
        else:
            pass
    return render_template(decision)

@app.route('/filter', methods = ["GET", "POST"])
def filter():
    if request.method == "POST":
        filters = request.form.getlist("filters")
        data = datacollection.datafilter('2019', *filters)
        stats = datacollection.main(data)
        machinelearning.initmodel(data, stats, filters)
        return redirect(url_for('model'))
    return render_template('filters.html')

@app.route('/model', methods = ["GET", "POST"])
def model():
    if request.method == "POST":
        model = request.form['model']
        results = get_model(model)
        model = results[0]
        stats = results[2]
        team1 = request.form['team1']
        team2 = request.form['team2']
        winner = predict_winner(team1, team2, model, stats)
        return render_template('model.html', prediction = winner)
    return render_template('model.html')


def get_team_stats(team, stats):
    teamrow = stats.loc[team, :]
    return teamrow

def get_model(model):
    model = "models/" + model
    with open(model, 'rb') as f:
        modl, filters, stats = pickle.load(f)
    return modl, filters, stats

def predict_winner(team1, team2, model, stats):
    # turn id back into name
    def convert_prediction(prediction):
        if prediction[0] == 1:
            # Team 1 Won
            return ID_TO_NAME.get(testrow[0])
        if prediction[0] == 0:
            # Team 2 Won
            return ID_TO_NAME.get(testrow[1])

    cols = ["Points Earned", "Points Lost", "Points Differential", "Points Differential Rank", "True Win %",
            "Map Potential %", "Map Potential % Rank"]
    types = ["Average Assault", "Average Control", "Average Hybrid", "Average Escort"]
    columns = []
    for i in types:
        columns.append([i + " " + j for j in cols])


    cols = ["Wins", "Losses", "Draws"]
    types = ["Total Assault", "Total Control", "Total Hybrid", "Total Escort"]
    for i in types:
        columns.append([i + " " + j for j in cols])

    columns = list(itertools.chain.from_iterable(columns))

    # create test data series
    newcol = ["Team 1", "Team 2"]

    # enter names of teams to get
    teamstats = pd.Series([team1, team2], index=newcol)

    # get all stats for each team
    awayrow = get_team_stats(teamstats[0], stats)
    homerow = get_team_stats(teamstats[1], stats)

    awayrow = awayrow[columns]
    homerow = homerow[columns]


    # convert columns to proper team placement
    awayrow = awayrow.rename(lambda x: "team1_" + x)
    homerow = homerow.rename(lambda x: "team2_" + x)

    # testrow = testrow.drop(labels=['Team 1', 'Team 2'])
    # turn name into id
    teamstats[0] = NAME_TO_ID.get(team1)
    teamstats[1] = NAME_TO_ID.get(team2)

    testrow = pd.concat([teamstats, awayrow, homerow])
    testrow = testrow[~testrow.index.str.contains("Rank")]

    prediction = model.predict([testrow])

    return convert_prediction(prediction)

if __name__ == "__main__":
    app.run(debug=True)