#!/usr/bin/env python
# coding: utf-8

# In[6]:


#https://baseballsavant.mlb.com/csv-docs#plate_x
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
cache.enable()

def Average(lst):
    return(sum(lst)/len(lst))

start_date = '2019-01-01' #yy/mm/dd
end_date = '2019-12-31'
data = statcast(start_date, end_date)
#print(data.head())

#### all stats from year 2020
#stats = batting_stats(2020)
#print(stats)
#print("==================================== AARON JUDGE ====================================")
#### Player lookup
#print(playerid_lookup('Judge', 'Aaron'))
#print()

#### Data on player
#player_data = statcast_batter('2016-04-01', '2017-07-15', player_id = 592450)
#print(player_data)
#df, player_info_dict = get_splits('judgeaa01', player_info = True)
#print(df)
#print()

##### Turns homeruns column to a list
#HRList = df['HR'].to_list() 
#print("Home runs in the last 365 days for Arron Judge: ", HRList[4])

#### Team batting stats for only 2019 season
#dataTeam = team_batting(2019)
#print(dataTeam)
#teams = team_ids(2019)
#batting = team_batting(2019).add_prefix('batting.')
#teams.merge(batting, left_on=['yearID', 'teamIDfg'], right_on=['batting.Season', 'batting.teamIDfg'])

#print("==================================== TEAM DATA ====================================")
#dataNYY = team_batting_bref('NYY', 2019)
#print(dataNYY)
#all_hits = dataNYY['HR'].to_list() 
#total = 0
#for num in all_hits:
#    total += int(num)
#print("Total home runs for NYY: ", total)

print("==================================== PITCH DATA NYY ==================================== \n")
dataNYY = team_batting_bref('NYY', 2019)
players = dataNYY['Name'].to_list() 
listPLayers = []    #### all NYY players
for playerName in players:             
    name = playerName.split()
    listPLayers.append(name)
####  Michael King, J.A. Happ empty data frame???

#### Stores players' ID in dict... Omits 2 players - no data 
playerNums = {}
for player in listPLayers:                      
    playerName = player[0] + " " + player[1]
    playerLookUp = playerid_lookup(player[1], player[0])
    playerNum = playerLookUp['key_mlbam'].to_list() 
    if len(playerNum) != 0:
        playerNums[playerName] = playerNum[0]   #### {'key': 'value'}
#print(playerNums)

#print(data.columns.get_loc('plate_x'))     #### finds index 
#print(data.columns.get_loc('plate_z'))     
#print(data.columns.get_loc('sz_top')) 
#print(data.columns.get_loc('sz_bot')) 

index = data.index
num_rows = len(index)

YankAtBats = []     #### all yank pitches  
xPosList = []       #### all x positions 
zPosList = []       #### all z positions 
DescList = []       #### all descriptions of pitches
topSZ = []          #### top of strike zone - predetermined
botSZ = []          #### bottom of strike zone - predetermined
pType = []          #### pitch type
Names = []          #### batter name
i = 0
gardyT = []
gardyB = []
for x in range(100000): #range(num_rows):    #ONLY FIRST 10000
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
        if name[0] == "Brett Gardner":
            gardyT.append((data.iloc[x]).iloc[50])
            gardyB.append((data.iloc[x]).iloc[51])
        atBat = [Names[i], xPosList[i], zPosList[i], pType[i], DescList[i]]
        YankAtBats.append(atBat)
        i += 1      

#### Classifications
classification = []
j = 0
for yankPitch in YankAtBats:
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
    j += 1

for z in range(len(YankAtBats)):
    YankAtBats[z].append(classification[z]) 

#### New data frame of all NYY pitches   
newdf = pd.DataFrame(YankAtBats, columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
print("FA - Fastball, CU - Curveball, FT - Two-seam Fastball, CH - Changeup, FC - Cutter, \nSL - Slider, FS - Splitter, KN - Knuckleball, FF - Four-seam Fastball \n")
print(newdf,"\n")


# In[30]:


#### can turn this into a function to do for each player
print("================================== BRETT GARDNER DATA ================================== \n")
avgTop = Average(gardyT)       
avgBot = Average(gardyB)  
Gardy = []
S_PitchCount = 0 # pitch count
S_Count = 0 # strike count
B_Count = 0 # ball count
goodStrikes = [] #list of tuples - (xpos, zpos)
badStrikes = []
goodBalls =[]
badBalls = []
for x in range(len(newdf)):  #### ************ add pitch coordinates at tuples to color code plot ******
    if ((newdf.iloc[x]).iloc[0]) == "Brett Gardner":
        Gardy.append(newdf.loc[x, :].values.flatten().tolist())
        S_PitchCount += 1
        if ((newdf.iloc[x]).iloc[5]) == "strike, good" or ((newdf.iloc[x]).iloc[5]) == "strike, bad":
            S_Count += 1
            if ((newdf.iloc[x]).iloc[5]) == "strike, good":
                goodStrikes.append(((newdf.iloc[x]).iloc[1], (newdf.iloc[x]).iloc[2]))
            else:
                badStrikes.append(((newdf.iloc[x]).iloc[1], (newdf.iloc[x]).iloc[2]))
        else:
            B_Count += 1
            if ((newdf.iloc[x]).iloc[5]) == "ball, good":
                goodBalls.append(((newdf.iloc[x]).iloc[1], (newdf.iloc[x]).iloc[2]))
            else:
                badBalls.append(((newdf.iloc[x]).iloc[1], (newdf.iloc[x]).iloc[2]))

#### Gardner Data Frame
GardyDF = pd.DataFrame(Gardy, columns = ['Name','xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
#print(GardyDF.head(len(GardyDF.index)).to_string())
print("FA - Fastball, CU - Curveball, FT - Two-seam Fastball, CH - Changeup, FC - Cutter, \nSL - Slider, FS - Splitter, KN - Knuckleball, FF - Four-seam Fastball \n")
print(GardyDF)
print()

percent_Good = len(goodStrikes) / S_Count
percent_Bad = len(goodBalls) /  B_Count
print("% of “good” strikes: ", round(percent_Good,3) )
print("% of “good” balls:",  round(percent_Bad,3) )
print("(% good strikes) + (% good balls): ", round((percent_Good + percent_Bad),3) )

#### Gardner Scatter Plot
#fig, ax = plt.subplots()
#plt.scatter(GardyDF['xPos'], GardyDF['zPos'])
#plt.xlabel("x position (ft)",fontweight ='bold', size=14)
#plt.ylabel("z position (ft)", fontweight ='bold',size=14)
#plt.title("Brett Gardner Pitch Data", fontweight ='bold',size=18)
#ax.add_patch(Rectangle((-0.79, 1.57), 1.58, 1.77,edgecolor = 'red',fill=False,lw=2))
#plt.show()

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlim(-1,1)
ax1.set_ylim(0,5)
for x in range(len(goodStrikes)):
    p1 = ax1.scatter(goodStrikes[x][0],goodStrikes[x][1], s=10, c='g', marker="o")
for y in range(len(badStrikes)):
    p2 = ax1.scatter(badStrikes[y][0], badStrikes[y][1], s=10, c='r', marker="o")
plt.title("Brett Gardner Strike Data", fontweight ='bold',size=18)
plt.legend([p1,p2], ["good strikes", "bad strikes"])
ax1.add_patch(Rectangle((-0.79, avgBot), 1.58, avgTop-avgBot ,edgecolor = 'red',fill=False,lw=2))
plt.show()

fig = plt.figure()
ax2 = fig.add_subplot(111)
ax2.set_xlim(-2.75,2.75)
ax2.set_ylim(0,5)
for x in range(len(goodBalls)):
    p21 = ax2.scatter(goodBalls[x][0],goodBalls[x][1], s=10, c='g', marker="o")
for y in range(len(badBalls)):
    p22 = ax2.scatter(badBalls[y][0], badBalls[y][1], s=10, c='r', marker="o", )
plt.title("Brett Gardner Ball Data", fontweight ='bold',size=18)
plt.legend([p21,p22], ["good balls", "bad balls"])
ax2.add_patch(Rectangle((-0.79, 1.57), 1.58, 1.77,edgecolor = 'red',fill=False,lw=2))
plt.show()


# In[29]:


print("================================ NYY PLAYER STAT DATA ================================ \n")
print("    Name\t    # pitches   # strikes   # balls  good strike%  good ball%    Sum")
for yank in playerNums:
    num_pitches = 0
    num_strikes = 0
    num_balls = 0
    num_good_strikes = 0
    num_good_balls = 0
    for x in range(len(newdf)):  
        if ((newdf.iloc[x]).iloc[0]) == yank:
            num_pitches += 1
            if ((newdf.iloc[x]).iloc[5]) == "strike, good" or ((newdf.iloc[x]).iloc[5]) == "strike, bad":
                num_strikes += 1
                if ((newdf.iloc[x]).iloc[5]) == "strike, good":
                    num_good_strikes += 1
            else:
                num_balls += 1
                if ((newdf.iloc[x]).iloc[5]) == "ball, good":
                    num_good_balls += 1
    if num_strikes != 0 and num_balls != 0:
        p_Good = num_good_strikes / num_strikes
        p_Bad = num_good_balls / num_balls
        print('{:<17s} {:>10} {:>10} {:>10} {:>10}% {:>10}% {:>10}%'.format(yank,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)))
        


# In[ ]:


# https://www.baseballprospectus.com/news/article/14098/spinning-yarn-the-real-strike-zone-part-2/
# z strike zone is 1.75 to 3.42 feet
# x strike zone is -0.71 to 0.71 feet
# top: 3.34, bottom: 1.57 ---> (-0.79, 1.57), 1, 1.77
# bottom left corner ->(x,y), width, height      
#https://www.geeksforgeeks.org/different-ways-to-create-pandas-dataframe/
#https://stackoverflow.com/questions/17812978/how-to-plot-two-columns-of-a-pandas-data-frame-using-points
#https://www.statology.org/matplotlib-rectangle/
#https://stackoverflow.com/questions/57246963/why-isnt-the-legend-in-matplotlib-correctly-displaying-the-colors

