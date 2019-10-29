import requests
import json

stats = requests.get("https://api.overwatchleague.com/stats/matches/30175/maps/8")
st = json.loads(stats.text)

def get_player_stats(teamID, playerID):
    for i in st["teams"]:
        if i["esports_team_id"]==teamID:
            for j in i["players"]:
                if j["esports_player_id"]== playerID:
                    ovrdamage = j["stats"][0]["value"]
                    ovrdeaths = j["stats"][1]["value"]
                    ovreliminations = j["stats"][2]["value"]
                    ovrhealing = j["stats"][3]["value"]


                    finalper = 0
                    index = 0
                    for k in j["heroes"]:
                        intdam = k["stats"][0]["value"]
                        intdea = k["stats"][1]["value"]
                        intelim = k["stats"][2]["value"]
                        intheal = k["stats"][3]["value"]

                        findam = (intdam/ovrdamage) * 100
                        findea = (intdea/ovrdeaths) * 100
                        finelim = (intelim/ovreliminations) * 100
                        finheal = (intheal/ovrhealing) * 100

                        totalper = findam + findea + finelim + finheal

                        if totalper > finalper:
                            finalper = totalper
                            index = k

                    hero_name = j["heroes"][index]["name"]




