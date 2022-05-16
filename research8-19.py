#!/usr/bin/env python
# coding: utf-8

# In[45]:


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

print("=============================== PITCH DATA NYY =============================== \n")
dataNYY = team_batting_bref('NYY', 2019)
players = dataNYY['Name'].to_list() 
listPLayers = []    #### all NYY players
for playerName in players:             
    name = playerName.split()
    listPLayers.append(name)

#### Stores players' ID in dict... Omits 2 players - no data 
playerNums = {}
for player in listPLayers:                      
    playerName = player[0] + " " + player[1]
    playerLookUp = playerid_lookup(player[1], player[0])
    playerNum = playerLookUp['key_mlbam'].to_list() 
    if len(playerNum) != 0:
        playerNums[playerName] = playerNum[0]   #### {'key': 'value'}

#print(data.columns.get_loc('plate_x'))     #### finds index 
#print(data.columns.get_loc('plate_z'))     
#print(data.columns.get_loc('sz_top')) 
#print(data.columns.get_loc('sz_bot')) 
#print("Balls: ",data.columns.get_loc('balls'))  #24
#print("Strikes: ",data.columns.get_loc('strikes'))  #25

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
Count_3_2 = []
i = 0
gardyT = []
gardyB = []
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
    YankAtBats[j].append(classification[j])
    j += 1

#### New data frame of all NYY pitches (size = 28512, last 53 bad)  
newdf = pd.DataFrame(YankAtBats[0:len(YankAtBats)-53], columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
print("FA - Fastball, CU - Curveball, FT - Two-seam Fastball, CH - Changeup, \nFC - Cutter, SL - Slider, FS - Splitter, KN - Knuckleball,\nFF - Four-seam Fastball \n")
print(newdf,"\n")


# In[44]:


#### BRETT GARDNER STATS
import math
print("============================ BRETT GARDNER DATA ============================ \n")
newGardyT = [x for x in gardyT if math.isnan(x) == False] #### removes nan
newGardyB = [y for y in gardyB if math.isnan(y) == False] #### removes nan
avgTop = round(Average(newGardyT),3)
avgBot = round(Average(newGardyB),3)
Gardy = []
S_PitchCount = 0 # pitch count
S_Count = 0 # strike count
B_Count = 0 # ball count
goodStrikes = [] #list of tuples - (xpos, zpos)
badStrikes = []
goodBalls =[]
badBalls = []
for x in range(len(newdf)):  #### add pitch coordinates as tuples to color code plot 
    if ((newdf.iloc[x]).iloc[0]) == "Brett Gardner":
        Gardy.append(newdf.loc[x, :].values.flatten().tolist()) # add row to new list
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
print("FA - Fastball, CU - Curveball, FT - Two-seam Fastball, CH - Changeup, \nFC - Cutter, SL - Slider, FS - Splitter, KN - Knuckleball,\nFF - Four-seam Fastball \n")
print(GardyDF)
print()

percent_Good = len(goodStrikes) / S_Count
percent_Bad = len(goodBalls) /  B_Count
print("% of “good” strikes: ", round(percent_Good,3) )
print("% of “good” balls:",  round(percent_Bad,3) )
print("(% good strikes) + (% good balls): ", round((percent_Good + percent_Bad),3) )

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
ax1.add_patch(Rectangle((-0.71, avgBot), 1.42, avgTop-avgBot ,edgecolor = 'red',fill=False,lw=2))
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
ax2.add_patch(Rectangle((-0.71, avgBot), 1.42, avgTop-avgBot ,edgecolor = 'red',fill=False,lw=2))
plt.show()


# In[39]:


#### ALL NYY PLAYER STATS
from IPython.core.display import display, HTML
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

display(HTML("<style>.container { width:100% !important; }</style>"))
print("============================ NYY PLAYER STAT DATA ============================ \n")
nyyList = []
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
    if num_strikes != 0 and num_balls != 0 and num_pitches >= 100:
        p_Good = num_good_strikes / num_strikes
        p_Bad = num_good_balls / num_balls
        nyyList.append([yank,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)])

NYYDF = pd.DataFrame(nyyList, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 

ax = NYYDF.plot.barh(x='Name', y='g_strike', figsize=(12, 8)) # Bar graph plot
plt.title("Good Strikes", fontweight ='bold',size=18)
plt.ylabel('Name', fontweight='bold', size=12)
plt.axvline(x=0.699, color='r', linestyle='--') # Draws average line
ax2 = NYYDF.plot.barh(x='Name', y='g_ball', figsize=(12, 8)) # Bar graph plot
plt.title("Good Balls", fontweight ='bold',size=18)
plt.ylabel('Name', fontweight='bold', size=12)
plt.axvline(x=0.673, color='r', linestyle='--') # Draws average line

print(color.BOLD + "\t\t\t    Ordered by name" + color.END)
print(NYYDF.sort_values(by='Name', ascending=True), "\n")
print(color.BOLD + "\t\t\t Ordered by pitches" + color.END)
sort = NYYDF.sort_values(by='Pitches', ascending=False)
print(sort, "\n")
print(color.BOLD + "\t\t\t Ordered by good strikes" + color.END)
sort1 = NYYDF.sort_values(by='g_strike', ascending=False)
print(sort1, "\n")
print(color.BOLD + "\t\t\t Ordered by good balls" + color.END)
sort2 = NYYDF.sort_values(by='g_ball', ascending=False)
print(sort2, "\n")
print(color.BOLD + "\t\t\t   Ordered by discernment score" + color.END)
sort3 = NYYDF.sort_values(by='DS', ascending=False)
print(sort3, "\n")

g_strike_AVG = NYYDF["g_strike"].mean() #### Gets average of whole column
g_ball_AVG = NYYDF["g_ball"].mean()
print("Team Good Strike Average: ", round(g_strike_AVG,3), "\nTeam Good Ball Average: ", round(g_ball_AVG,3))


# In[44]:


#### ONLY 3-2 COUNT PITCHES 
print("============================ NYY 3-2 COUNT DATA ============================ \n")
YankAtBats32 = []
for z in range(len(YankAtBats)):
    if Count_3_2[z] == 1:
        YankAtBats32.append(YankAtBats[z])

YankAtBats32df = pd.DataFrame(YankAtBats32[0:len(YankAtBats32)-5], columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
#print(YankAtBats32df,"\n")

nyyList2 = []
for yank in playerNums:
    num_pitches = 0
    num_strikes = 0
    num_balls = 0
    num_good_strikes = 0
    num_good_balls = 0
    for x in range(len(YankAtBats32df)):  
        if ((YankAtBats32df.iloc[x]).iloc[0]) == yank:
            num_pitches += 1
            if ((YankAtBats32df.iloc[x]).iloc[5]) == "strike, good" or ((YankAtBats32df.iloc[x]).iloc[5]) == "strike, bad":
                num_strikes += 1
                if ((YankAtBats32df.iloc[x]).iloc[5]) == "strike, good":
                    num_good_strikes += 1
            else:
                num_balls += 1
                if ((YankAtBats32df.iloc[x]).iloc[5]) == "ball, good":
                    num_good_balls += 1
    if num_strikes != 0 and num_balls != 0 and num_pitches >= 50:  #### min 50 pitches
        p_Good = num_good_strikes / num_strikes
        p_Bad = num_good_balls / num_balls
        nyyList2.append([yank,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)])

YankAtBats32df = pd.DataFrame(nyyList2, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 
print(color.BOLD + "\t\t\t    Ordered by name" + color.END)
print(YankAtBats32df.sort_values(by='Name', ascending=True), "\n")
print(color.BOLD + "\t\t\t Ordered by pitches" + color.END)
sort = YankAtBats32df.sort_values(by='Pitches', ascending=False)
print(sort, "\n")
print(color.BOLD + "\t\t\t Ordered by good strikes" + color.END)
sort1 = YankAtBats32df.sort_values(by='g_strike', ascending=False)
print(sort1, "\n")
print(color.BOLD + "\t\t\t Ordered by good balls" + color.END)
sort2 = YankAtBats32df.sort_values(by='g_ball', ascending=False)
print(sort2, "\n")
print(color.BOLD + "\t\t\t   Ordered by discernment score" + color.END)
sort3 = YankAtBats32df.sort_values(by='DS', ascending=False)
print(sort3, "\n")
g_strike_AVG = YankAtBats32df["g_strike"].mean() #### Gets average of whole column
g_ball_AVG = YankAtBats32df["g_ball"].mean()
print("Team Good Strike Average: ", round(g_strike_AVG,3), "\nTeam Good Ball Average: ", round(g_ball_AVG,3))


# In[45]:


#### ONLY FAST BALLS (2 and 4 seam)
print("============================ NYY FASTBALL DATA ============================ \n")
nyyList3 = []
for yank in playerNums:
    num_pitches = 0
    num_strikes = 0
    num_balls = 0
    num_good_strikes = 0
    num_good_balls = 0
    for x in range(len(newdf)):  
        if ((newdf.iloc[x]).iloc[0]) == yank and (((newdf.iloc[x]).iloc[3]) == "FT" or ((newdf.iloc[x]).iloc[3]) == "FF"): 
            num_pitches += 1
            if ((newdf.iloc[x]).iloc[5]) == "strike, good" or ((newdf.iloc[x]).iloc[5]) == "strike, bad":
                num_strikes += 1
                if ((newdf.iloc[x]).iloc[5]) == "strike, good":
                    num_good_strikes += 1
            else:
                num_balls += 1
                if ((newdf.iloc[x]).iloc[5]) == "ball, good":
                    num_good_balls += 1
    if num_strikes != 0 and num_balls != 0 and num_pitches >= 100:  #### Only using 100 here
        p_Good = num_good_strikes / num_strikes
        p_Bad = num_good_balls / num_balls
        nyyList3.append([yank,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)])

FastBallsDF = pd.DataFrame(nyyList3, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 

print(color.BOLD + "\t\t\t    Ordered by name" + color.END)
print(FastBallsDF.sort_values(by='Name', ascending=True), "\n")
print(color.BOLD + "\t\t\t Ordered by pitches" + color.END)
sort = FastBallsDF.sort_values(by='Pitches', ascending=False)
print(sort, "\n")
print(color.BOLD + "\t\t\t Ordered by good strikes" + color.END)
sort1 = FastBallsDF.sort_values(by='g_strike', ascending=False)
print(sort1, "\n")
print(color.BOLD + "\t\t\t Ordered by good balls" + color.END)
sort2 = FastBallsDF.sort_values(by='g_ball', ascending=False)
print(sort2, "\n")
print(color.BOLD + "\t\t\t   Ordered by discernment score" + color.END)
sort3 = FastBallsDF.sort_values(by='DS', ascending=False)
print(sort3, "\n")
g_strike_AVG = FastBallsDF["g_strike"].mean() #### Gets average of whole column
g_ball_AVG = FastBallsDF["g_ball"].mean()
print("Team Good Strike Average: ", round(g_strike_AVG,3), "\nTeam Good Ball Average: ", round(g_ball_AVG,3))


# In[43]:


#CU - Curveball, FT - Two-seam Fastball, CH - Changeup, 
#FC - Cutter, SL - Slider, FS - Splitter, KN - Knuckleball,
#FF - Four-seam Fastball 
FB = 0 
CU = 0
CH = 0
FC = 0
SL = 0
FS = 0
KN = 0
for x in range(len(newdf)):  
        if ((newdf.iloc[x]).iloc[3]) == "FT" or ((newdf.iloc[x]).iloc[3]) == "FF": 
            FB += 1
        if ((newdf.iloc[x]).iloc[3]) == "CU":
            CU += 1
        if ((newdf.iloc[x]).iloc[3]) == "CH":
            CH += 1
        if ((newdf.iloc[x]).iloc[3]) == "FC":
            FC += 1
        if ((newdf.iloc[x]).iloc[3]) == "SL":
            SL += 1
        if ((newdf.iloc[x]).iloc[3]) == "FS":
            FS += 1
        if ((newdf.iloc[x]).iloc[3]) == "KN":
            KN += 1
print("FB: ", FB)
print("CU: ", CU)
print("CH: ", CH)
print("FC: ", FC)
print("SL: ", SL)
print("FS: ", FS)
print("KN: ", KN)


# In[38]:


#### STATS FOR ALL OF MLB - Initial Data Frame
from pybaseball import playerid_reverse_lookup
allPlayers = [488726, 514888, 543807, 665742, 543685, 594809, 607208, 645302, 543228, 475582, 545350, 455139, 621043, 452678, 
              435062, 670541, 493329, 608324, 502210, 663656, 455117, 543037, 467827, 605452, 572821, 664353, 571578, 571431, 
              434671, 435559, 425844, 572191, 649557, 650402, 592450, 518934, 458731, 570482, 596142, 544369, 429665, 543305, 
              519317, 669242, 446308, 543939, 572761, 657557, 425877, 542303, 502671, 500874, 622168, 664056, 451594, 668227,
              544931, 656427, 457727, 425794, 453286, 571945, 596847, 502054, 640457, 642715, 595281, 621563, 541645, 519299, 
              518595, 621020, 452095, 594807, 455976, 518626, 518692, 645277, 660670, 459964, 435263, 542364, 458708, 457759, 
              571970, 572041, 621035, 669257, 571771, 608369, 501896, 641355, 592626, 607461, 621111, 664040, 588751, 465041, 
              641712, 572971, 666158, 448179, 443558, 593871, 596146, 543068, 503556, 593934, 650333, 641598, 592696, 595909, 
              622110, 650490, 647336, 431145, 628711, 547943, 570731, 592314, 477132, 571740, 593372, 543760, 572033, 543257, 
              501981, 595777, 592192, 621566, 656305, 657656, 670712, 664913, 669221, 592325, 606115, 456715, 519346, 460075, 
              669374, 519058, 518735, 663757, 519141, 543768, 605540, 641513, 621514, 500135, 543308, 650391, 660162, 572365, 
              600869, 474568, 641525, 664901, 570560, 641553, 650489, 606988, 594953, 456078, 641470, 547989, 622682, 408234, 
              641313, 595284, 596748, 656514, 656555, 547180, 656371, 623912, 435522, 434158, 543543, 514917, 517369, 446481, 
              445988, 542932, 621446, 592407, 621573, 594838, 489149, 645261, 608384, 516770, 643275, 572287, 546990, 624415, 
              605233, 571912, 641505, 663993, 621002, 628338, 542583, 620446, 591971, 475253, 642133, 606192, 545341, 640449, 
              645801, 425783, 624431, 592261, 642180, 608597, 669256, 596059, 542454, 641432, 462101, 643393, 623520, 518614, 
              663538, 605170, 575929, 596825, 664023, 450314, 656803, 608365, 502706, 656941, 543105, 605244, 573262, 643289, 
              576397, 456781, 607680, 664041, 474832, 605131, 542436, 502117, 621458, 518516, 596103, 446334, 457763, 572073, 
              543063, 641914, 622268, 623323, 596129, 553882, 641786, 572039, 572122, 543592, 641487, 643418, 621450, 620439, 
              543829, 605480, 607732, 518653, 622569, 591741, 606299, 518568, 657434, 592200, 571657, 466320, 624428, 621028, 
              596012, 642165, 606157, 553993, 607468, 570481, 571466, 592866, 641816, 458015, 642086, 425784, 467092, 621512, 
              641645, 642708, 434658, 605412, 624424, 624413, 663586, 476704, 664059, 605204, 607043, 429664, 592789, 453943, 
              606992, 640458, 641343, 668663, 664057, 506703, 594694, 644374, 502273, 623205, 600466, 656185, 605548, 596019, 
              608700, 614177, 467793, 605182, 621433, 664926, 600858, 625510, 596144, 643436, 656811, 641531, 534606, 553902, 
              664774, 624585, 641878, 591720, 488771, 460086, 593160, 435622, 602074, 656541, 621438, 641658, 624513, 460077, 
              605486, 592122, 642162, 658069, 606132, 541650, 444489, 641924, 641857, 475174, 547172, 502517, 571679, 453568, 
              656546, 605288, 646240, 605141, 621006, 642851, 592859, 598265, 593523, 571788, 543877, 444432, 542340, 600524, 
              641820, 669720, 593643, 519048, 502110, 593428, 491676, 641796, 668942, 572233, 500871, 649966, 647304, 642336, 
              605113, 527038, 605196, 543376, 543333, 592518, 571976, 594824, 502481, 605361, 608671, 571875, 592669, 622065, 
              620443, 592230, 571718, 664058, 600303, 664702, 596117, 571506, 642136, 621493, 592743, 594777, 608686, 647351,
              621532, 405395, 605612, 544725, 641477, 608475, 493596, 543510, 668670, 601713, 595751, 500743, 620453, 621107, 
              592761, 605421, 643376, 592273, 641856, 656713, 572228, 642731, 595981, 543309, 643396, 519222, 518960, 546991, 
              592660, 641933, 430935, 519390, 657277, 621005, 664238, 608596, 640461, 570267, 543377, 547179, 595798, 578428, 
              640447, 656725, 643230, 621086, 571467, 608331, 571927, 475247, 656669, 670032, 596115, 592346, 461829, 448801, 
              547004, 506702, 621466, 607752, 572008, 488671, 664034, 642736, 622534, 623180, 595978, 592662, 572070, 430945, 
              665120, 607345, 543045, 624133, 623168, 641154, 664068, 592826, 624512, 665489, 621219, 595222, 622046, 543101, 
              501571, 573186, 547379, 624577, 608723, 668676, 650619, 571448, 622608, 605200, 518542, 642082, 596105, 608348, 
              542882, 641778, 664199, 641684, 608070, 643217, 622786, 607536, 595881, 664192, 571917, 605397, 500779, 554430, 
              657141, 516416, 450306, 622491, 502624, 642221, 605474, 543148, 502188, 543532, 664119, 659275, 548389, 518792, 
              592206, 452657, 642607, 519203, 668804, 643446, 594798, 592767, 605490, 543475, 622492, 624641, 668800, 518876, 
              594577, 501659, 663567, 607572, 664062, 671790, 592567, 543294, 656605, 605400, 457803, 453284, 571974, 608718, 
              518618, 543243, 545121, 641541, 502190, 623993, 600474, 657061, 642423, 609275, 572362, 608577, 592663, 545333, 
              506433, 592178, 553869, 666971, 456501, 615698, 595879, 667498, 608379, 579328, 666182, 527054, 543548, 643290, 
              669160, 607625, 663978, 650859, 594835, 628317, 592863, 606466, 642547, 492802, 608371, 519144, 622694, 543401, 
              543022, 668678, 593958, 518586, 520471, 621529, 643265, 605137, 501303, 607391, 572816, 622666, 660271, 592885, 
              425772, 607333, 457708, 543351, 543302, 543557, 516782, 605446, 542979, 606956, 643565, 523253, 518633, 605347, 
              545361, 641584, 650893, 669222, 664854, 669060, 643615, 641829, 605280, 545358, 433587, 621097, 656954, 608337, 
              593576, 594965, 467055, 607054, 592612, 622772, 612672, 641149, 467100, 571980, 622072, 622075, 606162, 621381, 
              606131, 592879, 657041, 657571, 605156, 670329, 607231, 571697, 641312, 623214, 445055, 598271, 593334, 543135, 
              282332, 594986, 444482, 641755, 605119, 592348, 571437, 656577, 572020, 452254, 608566, 650644, 541600, 592644, 
              643327, 553878, 514913, 669456, 571670, 656887, 457915, 657566, 664247, 657145, 594840, 658792, 607200, 608385, 
              656794, 448855, 502026, 663432, 456051, 542255, 596451, 592351, 669270, 621199, 519293, 502043, 572863, 456701, 
              656222, 453172, 527048, 571918, 474463, 665487, 435079, 543118, 643493, 501985, 641627, 453562, 594311, 596119, 
              643603, 554340, 656308, 622797, 455104, 607219, 663465, 502042, 668683, 592444, 621453, 642207, 669214, 660761, 
              543089, 621249, 621141, 663776, 605135, 625643, 595956, 527049, 643354, 657077, 489334, 542921, 628452, 446321, 
              664874, 592332, 608334, 621311, 606273, 621439, 592680, 501381, 607223, 608339, 602922, 621244, 630111, 543606, 
              664045, 573135, 518452, 594987, 543699, 605276, 628356, 650671, 489119, 656977, 435064, 543432, 608344, 446263, 
              468504, 641745, 542960, 650813, 642545, 607644, 608336, 570240, 605164, 592741, 670970, 448281, 448602, 657140, 
              670950, 670456, 595375, 663531, 605508, 656252, 456488, 607776, 608717, 542963, 596001, 592620, 642098, 623352, 
              605253, 643338, 664208, 640470, 656257, 623364, 471865, 453281, 571539, 596043, 613534, 446868, 664196, 660853, 
              572140, 663898, 460576, 656288, 519008, 519076, 547982, 606424, 608638, 593528, 598286, 519455, 523260, 594011, 
              596057, 434378, 570256, 676606, 571946, 642558, 657053, 595465, 623184, 445926, 642721, 624414, 434778, 595191, 
              460026, 606959, 570632, 622766, 571745, 592229, 669203, 457705, 502239, 571510, 592717, 451192, 592468, 456665, 
              605513, 672773, 429719, 605151, 641851, 657097, 605154, 456124, 596112, 543281, 546318, 596133, 446359, 605498, 
              543001, 488768, 543883, 642397, 606149, 642073, 595453, 592387, 521655, 547170, 518553, 476451, 434538, 641941, 
              543193, 450203, 663423, 609280, 502570, 572143, 624419, 543194, 605538, 598284, 669738, 593647, 622103, 544928, 
              592716, 666198, 433589, 593423, 500208, 592865, 642003, 624407, 543776, 542881, 594988, 593700, 621559, 446372, 
              547888, 621389, 607229, 457918, 570666, 571863, 640460, 622226, 491696, 621261, 488721, 621550, 592791, 657024, 
              623454, 605520, 592685, 461314, 656775, 623167, 504379, 456030, 434670, 623149, 608715, 571595, 595885, 622554,
              642701, 592102, 658648, 593833, 643524, 458681, 543484, 600968, 650895, 656582, 630023, 598264, 519393, 584171,
              614173, 445276, 456034, 607192, 641438, 623515, 453064, 605439, 592779, 400085]
allAtBats = []
xPosList = []   
zPosList = []      
DescList = []      
topSZ = []          
botSZ = []         
pType = []          
Names = []          
#Count_3_2 = []
i = 0

data2 = playerid_reverse_lookup(allPlayers, key_type='mlbam')
#print(data2)
allFirstNames = data2['name_first'].to_list() 
allLastNames = data2['name_last'].to_list() 
allPlayerID = data2['key_mlbam'].to_list()
allNames = {}
j = 0
for player in allFirstNames:
    nameTemp = player + " " + allLastNames[j]
    if nameTemp not in allNames:
        allNames[nameTemp] = allPlayerID[j]
    j+=1

#print(allNames)

k = 0
i = 0
for player in allNames:
    ID = allNames[player]
    for x in range(100000):                              # range(num_rows): *****CHANGE BACK WHEN DOING FINAL
        tempID = (data.iloc[x]).iloc[6]
        if tempID == ID:
            Names.append(player)
            xPosList.append((data.iloc[x]).iloc[29])
            zPosList.append((data.iloc[x]).iloc[30])
            pType.append((data.iloc[x]).iloc[0])
            DescList.append((data.iloc[x]).iloc[9])
            topSZ.append((data.iloc[x]).iloc[50])
            botSZ.append((data.iloc[x]).iloc[51])
            atBat = [Names[i], xPosList[i], zPosList[i], pType[i], DescList[i]]
            allAtBats.append(atBat)
            i += 1 
#### Classifications
classification = []
j = 0
for pitch in allAtBats:
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
    allAtBats[j].append(classification[j])
    j += 1

ALLdf = pd.DataFrame(allAtBats, columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
print(ALLdf)


# In[37]:


#### STATS FOR ALL OF MLB - Discernment Scores
League = []
for batter in allNames:
    num_pitches = 0
    num_strikes = 0
    num_balls = 0
    num_good_strikes = 0
    num_good_balls = 0
    for x in range(len(ALLdf)): 
        if ((ALLdf.iloc[x]).iloc[0]) == batter:
            num_pitches += 1
            if ((ALLdf.iloc[x]).iloc[5]) == "strike, good" or ((ALLdf.iloc[x]).iloc[5]) == "strike, bad":
                num_strikes += 1
                if ((ALLdf.iloc[x]).iloc[5]) == "strike, good":
                    num_good_strikes += 1
            else:
                num_balls += 1
                if ((ALLdf.iloc[x]).iloc[5]) == "ball, good":
                    num_good_balls += 1
    if num_strikes != 0 and num_balls != 0 and num_pitches >= 100:
        p_Good = num_good_strikes / num_strikes
        p_Bad = num_good_balls / num_balls
        LeagueDF.append([batter,round(num_pitches,3) ,round(num_strikes,3), round(num_balls,3), round(p_Good,3),round(p_Bad,3),round((p_Good + p_Bad),3)])

LeagueDF = pd.DataFrame(League, columns = ['Name','Pitches', 'Strikes', 'Balls', 'g_strike', 'g_ball', 'DS']) 
print(LeagueDF)


# In[ ]:


#### NOTES/PRELIMINARY WORK
# z strike zone is 1.75 to 3.42 feet
# x strike zone is -0.71 to 0.71 feet
# top: 3.34, bottom: 1.57 ---> (-0.79, 1.57), 1, 1.77
# bottom left corner ->(x,y), width, height     
# https://www.baseballprospectus.com/news/article/14098/spinning-yarn-the-real-strike-zone-part-2/
# https://www.geeksforgeeks.org/different-ways-to-create-pandas-dataframe/
# https://stackoverflow.com/questions/17812978/how-to-plot-two-columns-of-a-pandas-data-frame-using-points
# https://www.statology.org/matplotlib-rectangle/
# https://stackoverflow.com/questions/57246963/why-isnt-the-legend-in-matplotlib-correctly-displaying-the-colors
# https://pythonexamples.org/pandas-dataframe-sort-by-column/#2
# https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python/8930747
# https://www.geeksforgeeks.org/change-figure-size-in-pandas-python/
# IMPORTANT: Cell -> Current Outputs -> Toggle Scrolling

#### all stats from year 2020
#stats = batting_stats(2020)
#print(stats)
#print("================================ AARON JUDGE ================================")
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

#print("================================ TEAM DATA ================================")
#dataNYY = team_batting_bref('NYY', 2019)
#print(dataNYY)
#all_hits = dataNYY['HR'].to_list() 
#total = 0
#for num in all_hits:
#    total += int(num)
#print("Total home runs for NYY: ", total)


# In[ ]:


#### FUNCTION FOR ALL TEAMS

def teamData(teamName):
    dataTeam = team_batting_bref(teamName, 2019)
    players = dataTeam['Name'].to_list() 
    listTeamPlayers = []    #### all team players
    
    
    
for playerName in players:             
    name = playerName.split()
    listPLayers.append(name)

#### Stores players' ID in dict... Omits 2 players - no data 
playerNums = {}
for player in listPLayers:                      
    playerName = player[0] + " " + player[1]
    playerLookUp = playerid_lookup(player[1], player[0])
    playerNum = playerLookUp['key_mlbam'].to_list() 
    if len(playerNum) != 0:
        playerNums[playerName] = playerNum[0]   #### {'key': 'value'}

#print(data.columns.get_loc('plate_x'))     #### finds index 
#print(data.columns.get_loc('plate_z'))     
#print(data.columns.get_loc('sz_top')) 
#print(data.columns.get_loc('sz_bot')) 
#print("Balls: ",data.columns.get_loc('balls'))  #24
#print("Strikes: ",data.columns.get_loc('strikes'))  #25

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
Count_3_2 = []
i = 0
gardyT = []
gardyB = []
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
    YankAtBats[j].append(classification[j])
    j += 1

#### New data frame of all NYY pitches (size = 28512, last 53 bad)  
newdf = pd.DataFrame(YankAtBats[0:len(YankAtBats)-53], columns = ['Name', 'xPos', 'zPos', 'Pitch Type', 'Given Description', 'Classification'])
print("FA - Fastball, CU - Curveball, FT - Two-seam Fastball, CH - Changeup, \nFC - Cutter, SL - Slider, FS - Splitter, KN - Knuckleball,\nFF - Four-seam Fastball \n")
print(newdf,"\n")

