#!/usr/bin/env python
# coding: utf-8

# In[17]:


# All MLB 
from pybaseball import statcast
from pybaseball import playerid_lookup
from pybaseball import statcast_pitcher, pitching_stats
from pybaseball import statcast_batter, batting_stats_range, batting_stats
from pybaseball import team_ids, teams, team_batting, team_batting_bref
from pybaseball import cache, standings, get_splits
import pandas as pd
import os
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatchess
import numpy as np
import math
cache.enable()
from IPython.core.display import display, HTML
class color:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def Average(lst):
    return(sum(lst)/len(lst))

start_date = '2019-01-01' #yy/mm/dd
end_date = '2019-12-31'
data = statcast(start_date, end_date) # Data for time between start and end date
data.dropna(subset = ['plate_x', 'plate_z', 'sz_top', 'sz_top', 'balls', 'strikes'], inplace=True) ##### DROPS ALL NaN ROWS

def TeamStats(teamName):
    Data = team_batting_bref(teamName, 2019) 
    players = Data['Name'].to_list() 
    listPLayers = []    #### all players on team
    for playerName in players:             
        name = playerName.split()
        listPLayers.append(name)
    #### Stores players' ID in dict... Omits players with no data 
    playerNums = {}
    for player in listPLayers:                      
        playerName = player[0] + " " + player[1]
        playerLookUp = playerid_lookup(player[1], player[0])
        playerNum = playerLookUp['key_mlbam'].to_list() 
        if len(playerNum) != 0:
            playerNums[playerName] = playerNum[0]   #### {'key': 'value'}
    num_rows = len(data.index)
    AtBats = []         #### all pitches  
    xPosList = []       #### all x positions 
    zPosList = []       #### all z positions 
    DescList = []       #### all descriptions of pitches
    topSZ = []          #### top of strike zone - predetermined
    botSZ = []          #### bottom of strike zone - predetermined
    pType = []          #### pitch type
    Names = []          #### batter name
    Count_3_2 = []
    i = 0
    for x in range(num_rows):  
        ID = (data.iloc[x]).iloc[6]
        name = [key for key, v in playerNums.items() if v == ID]
        if name != [] and name[0] in playerNums:
            Names.append(name[0])
            xPosList.append((data.iloc[x]).iloc[29])
            zPosList.append((data.iloc[x]).iloc[30])
            pType.append((data.iloc[x]).iloc[0])
            DescList.append((data.iloc[x]).iloc[9])
            topSZ.append((data.iloc[x]).iloc[50])
            botSZ.append((data.iloc[x]).iloc[51])
            if ((data.iloc[x]).iloc[24]) == 3 and ((data.iloc[x]).iloc[25]) == 2: #### pulls out all 3-2 counts
                Count_3_2.append(1)
            else:
                Count_3_2.append(0)
            atBat = [Names[i], xPosList[i], zPosList[i], pType[i], DescList[i]]
            AtBats.append(atBat)
            i += 1     
    #### Classifications
    classification = []
    j = 0
    for pitch in AtBats:
        ## strike
        if (-0.71 < xPosList[j] < 0.71) and (botSZ[j] < zPosList[j] < topSZ[j]):
            if DescList[j] == "hit_into_play" or DescList[j] == "swinging_strike" or DescList[j] == "foul" or DescList[j] == "swinging_strike_blocked" or DescList[j] == "foul_tip":
                classification.append("strike, good") # swung
            else:
                classification.append("strike, bad")  # didn't swing
        ## not strike
        else:
            if DescList[j] == "hit_into_play" or DescList[j] == "swinging_strike" or DescList[j] == "foul" or DescList[j] == "swinging_strike_blocked" or DescList[j] == "foul_tip":
                classification.append("ball, bad")    # swung
            else:
                classification.append("ball, good")   # didn't swing
        AtBats[j].append(classification[j])
        j += 1
    #### New data frame of all pitches
    newdf = pd.DataFrame(AtBats[0:len(AtBats)], columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
    #### Discernment Scores
    display(HTML("<style>.container { width:100% !important; }</style>"))
    mlbList = []
    for mlbPlayer in playerNums:
        num_pitches = 0
        num_strikes = 0
        num_balls = 0
        num_good_strikes = 0
        num_good_balls = 0
        for x in range(len(newdf)):  
            if ((newdf.iloc[x]).iloc[0]) == mlbPlayer:
                num_pitches += 1
                if ((newdf.iloc[x]).iloc[5]) == "strike, good" or ((newdf.iloc[x]).iloc[5]) == "strike, bad":
                    num_strikes += 1
                    if ((newdf.iloc[x]).iloc[5]) == "strike, good":
                        num_good_strikes += 1
                else:
                    num_balls += 1
                    if ((newdf.iloc[x]).iloc[5]) == "ball, good":
                        num_good_balls += 1
        if num_strikes != 0 and num_balls != 0 and num_pitches >= 100:
            p_Good = num_good_strikes / num_strikes
            p_Bad = num_good_balls / num_balls
            mlbList.append([mlbPlayer,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)])
    DF = pd.DataFrame(mlbList, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 
    print(color.BOLD + "\t\t   Top 10 Players Ordered by Discernment Score" + color.END)
    sort3 = DF.sort_values(by='DS', ascending=False)
    top = sort3.iloc[0].tolist()
    return top, sort3

#### CALL FUNCTION FOR TEAM NAME
# "FLA" - should be "MIA", "KAN" - should be "KC", "WAS" - should be "WSN"
MLBteamList = ["NYY", "ARI", "ATL",  "BAL", "BOS", "CHC", "CHW", "CIN", "CLE", "COL", "DET","MIA", "HOU", "KC", "LAA", "LAD", "MIL", "MIN", "NYM", "OAK", "PHI", "PIT", "SD", "SF", "SEA", "STL", "TB", "TEX", "TOR", "WSN"]
print("KEY: New York Yankees - NYY, Arizona Diamondbacks - ARI, Atlanta Braves - ATL, Baltimore Orioles - BAL, \n Boston Red Sox - BOS, Chicago Cubs - CHC, Chicago White Sox - CHW, Cincinnati Reds - CIN, Cleveland Indians - CLE, \n Colorado Rockies - COL, Detroit Tigers - DET, Florida Marlins - MIA, Houston Astros - HOU, Kansas City Royals - KC, \n Los Angeles Angels of Anaheim - LAA, Los Angeles Dodgers - LAD, Milwaukee Brewers - MIL, Minnesota Twins - MIN, \n New York Mets - NYM, Oakland Athletics - OAK, Philadelphia Phillies - PHI, Pittsburgh Pirates - PIT, \n San Diego Padres - SD, San Francisco Giants - SF, Seattle Mariners - SEA, St. Louis Cardinals - STL, \n Tampa Bay Rays - TB, Texas Rangers - TEX, Toronto Blue Jays - TOR, Washington Nationals - WSN \n")
print("============================== PRINTING STATS FOR MLB ==============================")
topPlayers = []
for i in range(len(MLBteamList)):
    print("\nTEAM: ", MLBteamList[i])
    topPlayer, wholeTeam = TeamStats(MLBteamList[i])
    topPlayers.append(topPlayer)
    print(wholeTeam)
    
print(color.BOLD + "\n\t\t   Top MLB Players Ordered by Discernment Score" + color.END)
MLBDF = pd.DataFrame(topPlayers, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 
MLBsort = MLBDF.sort_values(by='DS', ascending=False)
print(MLBsort)


# In[ ]:




