#Getting proper libraries
import pandas as pd
import numpy as np
import re

from constants import MAP_TYPE


def get_stats(thelist, i):
    # Columns that will be recorded
    map_colums = ["wins", "losses", "draws", "times_played", "average_points_earned",
                  "average_points_lost", "average_points_differential", "win_perc", "true_perc", "map_potential_perc"]

    name = thelist[0]["name"]
    loss = round(0, 3)
    win = round(0, 3)
    draw = round(0, 3)
    points_earned = round(0, 3)
    points_given = round(0, 3)
    map_potential = round(0, 3)

    total = len(thelist)
    for game in thelist:
        if game.winner != i:
            if game.winner == "draw":
                draw += 1
                points_earned += game.loser_score
                points_given += game.winner_score
                pwon = game.loser_score
                plos = game.winner_score
            else:
                loss += 1
                points_earned += game.loser_score
                points_given += game.winner_score
                pwon = game.loser_score
                plos = game.winner_score

        else:
            win += 1
            points_earned += game.winner_score
            points_given += game.loser_score
            pwon = game.loser_score
            plos = game.winner_score

        if pwon > plos:
            map_potential += 1
        else:
            try:
                map_potential += (pwon / plos)
            except ZeroDivisionError:
                map_potential += 0

    win_per = round((win / total) * 100, 3)
    true_per = round(((win + (draw / 2)) / total) * 100, 3)
    avg_points_earned = round(points_earned / total, 3)
    avg_points_given = round(points_given / total, 3)
    avg_point_diff = round(avg_points_earned - avg_points_given, 3)
    true_map_potential = round(map_potential / total, 3)

    colums = [name + "_" + w for w in map_colums]

    map_data = pd.Series([win, loss, draw, total,
                          avg_points_earned, avg_points_given, avg_point_diff, win_per, true_per,
                          true_map_potential], colums)
    return map_data


#helper function to aggregate data across the map type, and returns statictics
def sum_rows(maptype, name, stats):
    times_played = [i for i in maptype if "times_played" in i]
    times_playedtotal = stats[times_played].sum(axis=1)

    wins = [i for i in maptype if "wins" in i]
    winstotal = stats[wins].sum(axis=1)

    loss = [i for i in maptype if "losses" in i]
    losstotal = stats[loss].sum(axis=1)

    draw = [i for i in maptype if "draws" in i]
    drawtotal = stats[draw].sum(axis=1)

    earned = [i for i in maptype if "average_points_earned" in i]
    earnedtotal = stats[earned].mean(axis=1)

    lost = [i for i in maptype if "average_points_lost" in i]
    losttotal = stats[lost].mean(axis=1)

    differ = [i for i in maptype if "average_points_differential" in i]
    differtotal = stats[differ].mean(axis=1)
    sa = pd.DataFrame(data=differtotal)
    sa["total"] = differtotal
    differrank = sa["total"].rank(ascending=False, method="min")

    winperctotal = (winstotal / times_playedtotal) * 100
    sa["total"] = winperctotal
    winpercrank = sa["total"].rank(ascending=False, method="min")

    trueperctotal = ((winstotal + (drawtotal / 2)) / times_playedtotal) * 100
    sa["total"] = trueperctotal
    truepercrank = sa["total"].rank(ascending=False, method="min")

    cows = [i for i in maptype if "map_potential_perc" in i and "Rank" not in i]
    cowstotal = stats[cows].mean(axis=1)
    sa["total"] = cowstotal
    cowsrank = sa["total"].rank(ascending=False, method="min")

    if name == "Assault":
        stats.insert(stats.columns.get_loc("Volskaya Industries_map_potential_perc_rank") + 1, "Total Assault Wins",
                     winstotal)
        stats.insert(stats.columns.get_loc("Total Assault Wins") + 1, "Total Assault Losses", losstotal)
        stats.insert(stats.columns.get_loc("Total Assault Losses") + 1, "Total Assault Draws", drawtotal)
        stats.insert(stats.columns.get_loc("Total Assault Draws") + 1, "Total Assault Played", times_playedtotal)
        stats.insert(stats.columns.get_loc("Total Assault Played") + 1, "Average Assault Points Earned", earnedtotal)
        stats.insert(stats.columns.get_loc("Average Assault Points Earned") + 1, "Average Assault Points Lost",
                     losttotal)
        stats.insert(stats.columns.get_loc("Average Assault Points Lost") + 1, "Average Assault Points Differential",
                     differtotal)
        stats.insert(stats.columns.get_loc("Average Assault Points Differential") + 1,
                     "Average Assault Points Differential Rank", differrank)
        stats.insert(stats.columns.get_loc("Average Assault Points Differential Rank") + 1, "Average Assault Win %",
                     winperctotal)
        stats.insert(stats.columns.get_loc("Average Assault Win %") + 1, "Average Assault Win % Rank", winpercrank)
        stats.insert(stats.columns.get_loc("Average Assault Win % Rank") + 1, "Average Assault True Win %",
                     trueperctotal)
        stats.insert(stats.columns.get_loc("Average Assault True Win %") + 1, "Average Assault True Win % Rank",
                     truepercrank)
        stats.insert(stats.columns.get_loc("Average Assault True Win % Rank") + 1, "Average Assault Map Potential %",
                     cowstotal)
        stats.insert(stats.columns.get_loc("Average Assault Map Potential %") + 1,
                     "Average Assault Map Potential % Rank", cowsrank)

    elif name == "Control":
        stats.insert(stats.columns.get_loc("Oasis_map_potential_perc_rank") + 1, "Total Control Wins", winstotal)
        stats.insert(stats.columns.get_loc("Total Control Wins") + 1, "Total Control Losses", losstotal)
        stats.insert(stats.columns.get_loc("Total Control Losses") + 1, "Total Control Draws", drawtotal)
        stats.insert(stats.columns.get_loc("Total Control Draws") + 1, "Total Control Played", times_playedtotal)
        stats.insert(stats.columns.get_loc("Total Control Played") + 1, "Average Control Points Earned", earnedtotal)
        stats.insert(stats.columns.get_loc("Average Control Points Earned") + 1, "Average Control Points Lost",
                     losttotal)
        stats.insert(stats.columns.get_loc("Average Control Points Lost") + 1, "Average Control Points Differential",
                     differtotal)
        stats.insert(stats.columns.get_loc("Average Control Points Differential") + 1,
                     "Average Control Points Differential Rank", differrank)
        stats.insert(stats.columns.get_loc("Average Control Points Differential Rank") + 1, "Average Control Win %",
                     winperctotal)
        stats.insert(stats.columns.get_loc("Average Control Win %") + 1, "Average Control Win % Rank", winpercrank)
        stats.insert(stats.columns.get_loc("Average Control Win % Rank") + 1, "Average Control True Win %",
                     trueperctotal)
        stats.insert(stats.columns.get_loc("Average Control True Win %") + 1, "Average Control True Win % Rank",
                     truepercrank)
        stats.insert(stats.columns.get_loc("Average Control True Win % Rank") + 1, "Average Control Map Potential %",
                     cowstotal)
        stats.insert(stats.columns.get_loc("Average Control Map Potential %") + 1,
                     "Average Control Map Potential % Rank", cowsrank)

    elif name == "Hybrid":
        stats.insert(stats.columns.get_loc("Numbani_map_potential_perc_rank") + 1, "Total Hybrid Wins", winstotal)
        stats.insert(stats.columns.get_loc("Total Hybrid Wins") + 1, "Total Hybrid Losses", losstotal)
        stats.insert(stats.columns.get_loc("Total Hybrid Losses") + 1, "Total Hybrid Draws", drawtotal)
        stats.insert(stats.columns.get_loc("Total Hybrid Draws") + 1, "Total Hybrid Played", times_playedtotal)
        stats.insert(stats.columns.get_loc("Total Hybrid Played") + 1, "Average Hybrid Points Earned", earnedtotal)
        stats.insert(stats.columns.get_loc("Average Hybrid Points Earned") + 1, "Average Hybrid Points Lost", losttotal)
        stats.insert(stats.columns.get_loc("Average Hybrid Points Lost") + 1, "Average Hybrid Points Differential",
                     differtotal)
        stats.insert(stats.columns.get_loc("Average Hybrid Points Differential") + 1,
                     "Average Hybrid Points Differential Rank", differrank)
        stats.insert(stats.columns.get_loc("Average Hybrid Points Differential Rank") + 1, "Average Hybrid Win %",
                     winperctotal)
        stats.insert(stats.columns.get_loc("Average Hybrid Win %") + 1, "Average Hybrid Win % Rank", winpercrank)
        stats.insert(stats.columns.get_loc("Average Hybrid Win % Rank") + 1, "Average Hybrid True Win %", trueperctotal)
        stats.insert(stats.columns.get_loc("Average Hybrid True Win %") + 1, "Average Hybrid True Win % Rank",
                     truepercrank)
        stats.insert(stats.columns.get_loc("Average Hybrid True Win % Rank") + 1, "Average Hybrid Map Potential %",
                     cowstotal)
        stats.insert(stats.columns.get_loc("Average Hybrid Map Potential %") + 1, "Average Hybrid Map Potential % Rank",
                     cowsrank)

    elif name == "Escort":
        stats.insert(stats.columns.get_loc("Watchpoint: Gibraltar_map_potential_perc_rank") + 1, "Total Escort Wins",
                     winstotal)
        stats.insert(stats.columns.get_loc("Total Escort Wins") + 1, "Total Escort Losses", losstotal)
        stats.insert(stats.columns.get_loc("Total Escort Losses") + 1, "Total Escort Draws", drawtotal)
        stats.insert(stats.columns.get_loc("Total Escort Draws") + 1, "Total Escort Played", times_playedtotal)
        stats.insert(stats.columns.get_loc("Total Escort Played") + 1, "Average Escort Points Earned", earnedtotal)
        stats.insert(stats.columns.get_loc("Average Escort Points Earned") + 1, "Average Escort Points Lost", losttotal)
        stats.insert(stats.columns.get_loc("Average Escort Points Lost") + 1, "Average Escort Points Differential",
                     differtotal)
        stats.insert(stats.columns.get_loc("Average Escort Points Differential") + 1,
                     "Average Escort Points Differential Rank", differrank)
        stats.insert(stats.columns.get_loc("Average Escort Points Differential Rank") + 1, "Average Escort Win %",
                     winperctotal)
        stats.insert(stats.columns.get_loc("Average Escort Win %") + 1, "Average Escort Win % Rank", winpercrank)
        stats.insert(stats.columns.get_loc("Average Escort Win % Rank") + 1, "Average Escort True Win %", trueperctotal)
        stats.insert(stats.columns.get_loc("Average Escort True Win %") + 1, "Average Escort True Win % Rank",
                     truepercrank)
        stats.insert(stats.columns.get_loc("Average Escort True Win % Rank") + 1, "Average Escort Map Potential %",
                     cowstotal)
        stats.insert(stats.columns.get_loc("Average Escort Map Potential %") + 1, "Average Escort Map Potential % Rank",
                     cowsrank)

    else:
        pass

def datanew(df):
    # Splits dataframe into each individual game
    games = []
    for k, d in df.groupby("match_id"):
        games.append(d)

    columns = ['id', 'date', 'stage', 'winning_team', 'winner_score', 'loser_score', 'losing_team']
    allgames = []
    # Iterates through the games to narrow data
    for i in games:
        maps = []
        winner_score = 0
        loser_score = 0
        colu = ["name", "type", "winner", "winner_score", "loser_score", "loser"]
        date = i.round_start_time.iloc[0]
        stage = i.stage.iloc[0]
        matchid = i.match_id.iloc[0]
        winning_team = i.match_winner.iloc[0]
        if winning_team == i.map_winner.iloc[0]:
            losing_team = i.map_loser.iloc[0]
        else:
            losing_team = i.map_winner.iloc[0]
        for k, d in i.groupby("game_number"):
            mapa = d.iloc[0]
            map_number = mapa.game_number
            map_name = mapa.map_name
            if map_name == "Lijiang Tower":
                map_type = "Control"
            elif map_name == "Temple of Anubis":
                map_type = "Assault"
            elif map_name == "Watchpoint: Gibraltar":
                map_type = "Escort"
            else:
                map_type = MAP_TYPE.get(map_name)
            map_winner = mapa.map_winner
            map_loser = mapa.map_loser
            map_winner_score = mapa.winning_team_final_map_score
            map_loser_score = mapa.losing_team_final_map_score
            colum = ["map_" + str(map_number) + "_" + j for j in colu]
            mapdata = pd.Series([map_name, map_type, map_winner, map_winner_score, map_loser_score, map_loser], colum)
            maps.append(mapdata)
            if map_winner == winning_team:
                winner_score += 1
            elif map_winner == losing_team:
                loser_score += 1
            else:
                continue
        data = pd.Series([matchid, date, stage, winning_team, winner_score, loser_score, losing_team], columns)
        for item in maps:
            data = pd.concat([data, item])

        allgames.append(data)
    gamers = pd.DataFrame(allgames)
    gamers = gamers.set_index("id")
    gamers["date"] = pd.to_datetime(gamers.date)
    gamers = gamers.sort_values(by="date")

    return gamers

def datafilter(year, *keywords):
    #Reads the CSV and loads it into a dataframe
    df= pd.read_csv("match_map_stats.csv")

    #selecting which one to use
    df = df[df["round_end_time"].str.contains(year)]


    #Created a Filtration System to filter out certain stats
    for keyword in keywords[0:]:
        df = df[~df.stage.str.contains(keyword)]

    df = datanew(df)
    return df

def main(gamers):
    teamnames = ['Atlanta Reign', 'Boston Uprising', 'Chengdu Hunters', 'Dallas Fuel', 'Florida Mayhem',
                 'Guangzhou Charge', 'Hangzhou Spark', 'Houston Outlaws', 'London Spitfire', 'Los Angeles Gladiators',
                 'Los Angeles Valiant', 'New York Excelsior', 'Paris Eternal', 'Philadelphia Fusion', 'San Francisco Shock',
                 'Seoul Dynasty', 'Shanghai Dragons', 'Toronto Defiant', 'Vancouver Titans', 'Washington Justice']
    team_series = []

    # Filtering Dataframe to numerical data
    colums = ["winning_team", "winner_score", "losing_team", "loser_score",
              "map_1_name", "map_1_type", "map_1_winner", "map_1_winner_score", "map_1_loser_score", "map_1_loser",
              "map_2_name", "map_2_type", "map_2_winner", "map_2_winner_score", "map_2_loser_score", "map_2_loser",
              "map_3_name", "map_3_type", "map_3_winner", "map_3_winner_score", "map_3_loser_score", "map_3_loser",
              "map_4_name", "map_4_type", "map_4_winner", "map_4_winner_score", "map_4_loser_score", "map_4_loser",
              "map_5_name", "map_5_type", "map_5_winner", "map_5_winner_score", "map_5_loser_score", "map_5_loser"]

    df = gamers[colums]


    # iterates through each team and collects all map statistics
    for i in teamnames:
        control = []
        assault = []
        hybrid = []
        escort = []
        teamdf = df[df.eq(i).any(1)]
        for index, row in teamdf.iterrows():
            for column in row.iteritems():
                if column[0].find("type") > -1:
                    map_name = column[0].replace("_type", "")
                    if isinstance(column[1], str):
                        index = ["name", "type", "winner", "winner_score", "loser_score", "loser"]
                        if column[1].find("Control") > -1:
                            data = row[(map_name + "_name"):(map_name + "_loser")]
                            data.index = index
                            control.append(data)
                        elif column[1].find("Assault") > -1:
                            data = row[(map_name + "_name"):(map_name + "_loser")]
                            data.index = index
                            assault.append(data)
                        elif column[1].find("Hybrid") > -1:
                            data = row[(map_name + "_name"):(map_name + "_loser")]
                            data.index = index
                            hybrid.append(data)
                        elif column[1].find("Escort") > -1:
                            data = row[(map_name + "_name"):(map_name + "_loser")]
                            data.index = index
                            escort.append(data)
                        else:
                            continue
        # Assault
        hanamura = []
        horizon = []
        paris = []
        temple = []
        volskaya = []

        # Control
        busan = []
        ilios = []
        lijiang = []
        nepal = []
        oasis = []

        # Hybrid
        blizzard = []
        eichenwalde = []
        hollywood = []
        king = []
        numbani = []

        # Escort
        dorado = []
        havana = []
        junkertown = []
        rialto = []
        route = []
        gibraltar = []

        for j in assault:
            if j["name"].find("Hanamura") > -1:
                hanamura.append(j)
            elif j["name"].find("Horizon Lunar Colony") > -1:
                horizon.append(j)
            elif j["name"].find("Paris") > -1:
                paris.append(j)
            elif j["name"].find("Temple of Anubis") > -1:
                temple.append(j)
            elif j["name"].find("Volskaya Industries") > -1:
                volskaya.append(j)
            else:
                continue
        assault_data = pd.concat([get_stats(hanamura, i),
                                  get_stats(horizon, i),
                                  get_stats(paris, i),
                                  get_stats(temple, i),
                                  get_stats(volskaya, i)])

        for j in control:
            if j["name"].find("Busan") > -1:
                busan.append(j)
            elif j["name"].find("Ilios") > -1:
                ilios.append(j)
            elif j["name"].find("Lijiang Tower") > -1:
                lijiang.append(j)
            elif j["name"].find("Nepal") > -1:
                nepal.append(j)
            elif j["name"].find("Oasis") > -1:
                oasis.append(j)
            else:
                continue
        control_data = pd.concat([get_stats(busan, i),
                                  get_stats(ilios, i),
                                  get_stats(lijiang, i),
                                  get_stats(nepal, i),
                                  get_stats(oasis, i)
                                  ])

        for j in hybrid:
            if j["name"].find("Blizzard World") > -1:
                blizzard.append(j)
            elif j["name"].find("Eichenwalde") > -1:
                eichenwalde.append(j)
            elif j["name"].find("Hollywood") > -1:
                hollywood.append(j)
            elif j["name"].find("King's Row") > -1:
                king.append(j)
            elif j["name"].find("Numbani") > -1:
                numbani.append(j)
            else:
                continue
        hybrid_data = pd.concat([get_stats(blizzard, i),
                                 get_stats(eichenwalde, i),
                                 get_stats(hollywood, i),
                                 get_stats(king, i),
                                 get_stats(numbani, i)])

        for j in escort:
            if j["name"].find("Dorado") > -1:
                dorado.append(j)
            elif j["name"].find("Havana") > -1:
                havana.append(j)
            elif j["name"].find("Junkertown") > -1:
                junkertown.append(j)
            elif j["name"].find("Rialto") > -1:
                rialto.append(j)
            elif j["name"].find("Route 66") > -1:
                route.append(j)
            elif j["name"].find("Watchpoint: Gibraltar") > -1:
                gibraltar.append(j)
            else:
                continue
        escort_data = pd.concat([get_stats(dorado, i),
                                 get_stats(havana, i),
                                 get_stats(junkertown, i),
                                 get_stats(rialto, i),
                                 get_stats(route, i),
                                 get_stats(gibraltar, i)])

        complete_data = pd.concat([assault_data, control_data, hybrid_data, escort_data])
        team_name = pd.Series(i, index=["Team Name"])
        complete_data = pd.concat([team_name, complete_data])
        team_series.append(complete_data)

        # clearing all previous items in list, as the list is reused
        assault.clear()
        control.clear()
        hybrid.clear()
        escort.clear()

    #Turn data into dataframe
    datadf = pd.DataFrame(team_series)

    #Assign map names to each series of data
    map_names = ["Busan","Ilios","Lijiang Tower","Nepal","Oasis",
                 "Hanamura","Horizon Lunar Colony","Paris","Temple of Anubis","Volskaya Industries",
                 "Blizzard World","Eichenwalde","Hollywood","King's Row","Numbani",
                 "Dorado","Havana","Junkertown","Rialto","Route 66","Watchpoint: Gibraltar"]

    #Adds Percentages and Rankings for each team
    for stringtest in map_names:
        wincol = datadf[stringtest+"_win_perc"].rank(ascending = False, method = "min")
        truecol = datadf[stringtest+"_true_perc"].rank(ascending = False, method = "min")
        mappolcol = datadf[stringtest+"_map_potential_perc"].rank(ascending = False, method = "min")
        datadf.insert(datadf.columns.get_loc(stringtest+"_win_perc") + 1, stringtest+"_win_perc_rank", wincol )
        datadf.insert(datadf.columns.get_loc(stringtest+"_true_perc") + 1, stringtest+"_true_perc_rank", truecol )
        datadf.insert(datadf.columns.get_loc(stringtest+"_map_potential_perc") + 1, stringtest+"_map_potential_perc_rank", mappolcol)

    # renaming for writeability
    stats = datadf



    # filtering maps based on map type
    for i in stats.columns:
        if re.search("Hanamura\B", i) or re.search("Horizon Lunar Colony\B", i) or re.search("Paris\B", i) or re.search(
                "Temple of Anubis\B", i) or re.search("Volskaya Industries\B", i):
            assault.append(i)
        elif re.search("Busan\B", i) or re.search("Ilios\B", i) or re.search("Lijiang Tower\B", i) or re.search("Nepal\B",
                                                                                                                i) or re.search(
                "Oasis\B", i):
            control.append(i)
        elif re.search("Blizzard World\B", i) or re.search("Eichenwalde\B", i) or re.search("Hollywood\B", i) or re.search(
                "King's Row\B", i) or re.search("Numbani\B", i):
            hybrid.append(i)
        elif re.search("Dorado\B", i) or re.search("Havana\B", i) or re.search("Junkertown\B", i) or re.search("Rialto\B",
                                                                                                               i) or re.search(
                "Route 66\B", i) or re.search("Watchpoint: Gibraltar\B", i):
            escort.append(i)
        else:
            continue

    sum_rows(assault, "Assault", stats)
    sum_rows(control, "Control", stats)
    sum_rows(hybrid, "Hybrid", stats)
    sum_rows(escort, "Escort", stats)

    #This is primarily a playoff check to remove teams who did not participate in playoffs or stage playoffs
    stats = stats[np.isfinite(stats["Average Escort Win %"])]
    stats = stats.set_index("Team Name")

    return stats

if __name__ == "__main__":
    df = datafilter('2019')
    df = main(df)

    #converts all data to a csv
    df.to_csv("statsnew.csv")