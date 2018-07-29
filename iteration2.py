import pandas as pd
import urllib2
import numpy as np
import math

from bs4 import BeautifulSoup

np.set_printoptions(threshold=np.inf)


def getTeamList():
    req = urllib2.Request("https://www.masseyratings.com/cf/compare.htm")
    response = urllib2.urlopen(req)

    html_doc = response.read()
    soup = BeautifulSoup(html_doc,'html.parser')
    for link in soup.find_all('a'):
        print link.text

def numTeamsInGameList():
    dataSet = pd.read_csv("gamelist.csv")

    teamDict = []

    for i in range(0,873):
        if dataSet['Winner'][i] not in teamDict:
            teamDict.append(dataSet['Winner'][i])
        if dataSet['Loser'][i] not in teamDict:
            teamDict.append(dataSet['Loser'][i])

    return len(teamDict)

def getTeamListArray():
    dataSet = pd.read_csv("teamList.csv")

    teamList = []

    for index, row in dataSet.iterrows():
        teamList.append(row[0])

    return teamList

def getTeamToIndexMap():
    teamList = getTeamListArray()

    teamToIndex = {}

    for index,team in enumerate(teamList):
        teamToIndex[team] = index

    return teamToIndex

def getIndexToTeamMap():
    teamList = getTeamListArray()

    teamToIndex = {}

    for index, team in enumerate(teamList):
        teamToIndex[index] = team

    return teamToIndex

def getGamesPlayed(team):
    dataSet = pd.read_csv("gamelist.csv")

    gamesPlayed = 0

    for i in range(0,873):
        if dataSet['Winner'][i] == team:
            gamesPlayed = gamesPlayed + 1
        if dataSet['Loser'][i] == team:
            gamesPlayed = gamesPlayed + 1

    return gamesPlayed

def getGamesLost(team):
    dataSet = pd.read_csv("gamelist.csv")

    gamesLost = 0

    for i in range(0, 873):
        if dataSet['Loser'][i] == team:
            gamesLost = gamesLost + 1

    return gamesLost

def getGamesWon(team):
    dataSet = pd.read_csv("gamelist.csv")

    gamesWon = 0

    for i in range(0, 873):
        if (dataSet['Winner'][i] == team) and (dataSet['Loser'][i] in getTeamListArray()):
            gamesWon = gamesWon + 1

    return gamesWon

def ToReducedRowEchelonForm( M):
    if not M.any(): return
    lead = 0
    rowCount = len(M)
    columnCount = len(M[0])
    for r in range(rowCount):
        if lead >= columnCount:
            return
        i = r
        while M[i][lead] == 0:
            i += 1
            if i == rowCount:
                i = r
                lead += 1
                if columnCount == lead:
                    return
        M[i],M[r] = M[r],M[i]
        lv = M[r][lead]
        M[r] = [ mrx / float(lv) for mrx in M[r]]
        for i in range(rowCount):
            if i != r:
                lv = M[i][lead]
                M[i] = [ iv - lv*rv for rv,iv in zip(M[r],M[i])]
        lead += 1

dataSet = pd.read_csv("gamelist.csv")
goodTeamNum = len(getTeamListArray())
totalTeamList = numTeamsInGameList()
goodTeamList = getTeamListArray()
totalGames = 15

teamToIndexMap = getTeamToIndexMap()
indexToTeamMap = getIndexToTeamMap()

junctureMatrix = np.zeros((goodTeamNum,goodTeamNum))

for i in range(0,goodTeamNum):
    junctureMatrix[i][i]=math.pow(totalGames,2)
# np.fill_diagonal(junctureMatrix,2*totalGames)

lossVector = np.asarray([(math.pow(totalGames,2)/2) for x in getTeamListArray()])

for index, row in dataSet.iterrows():
    if (row[0] in goodTeamList)and(row[2] in goodTeamList):
        indexWinner = teamToIndexMap[row[0]]
        indexLoser = teamToIndexMap[row[2]]
        junctureMatrix[indexWinner][indexLoser] = -1 * getGamesWon(indexToTeamMap[indexLoser])
        junctureMatrix[indexLoser][indexWinner] = -1 * getGamesLost(indexToTeamMap[indexWinner])
        lossVector[indexLoser] -= getGamesLost(indexToTeamMap[indexWinner])
    if (row[0] not in goodTeamList):
        if (row[2] in goodTeamList):
            indexLoser = teamToIndexMap[row[2]]
            lossVector[indexLoser] -= totalGames

lossVector = lossVector.reshape(lossVector.shape[0],-1)

rrefMatrix = np.concatenate((junctureMatrix,lossVector),axis=1)
ToReducedRowEchelonForm(rrefMatrix)

teamToRatingMap = {}

for i in range(0,rrefMatrix.shape[0]):
    teamToRatingMap[indexToTeamMap[i]]=rrefMatrix[i,128]

sorted_x = sorted(teamToRatingMap, key=teamToRatingMap.get)
for k,v in enumerate(reversed(sorted_x)):
    print k+1,v, teamToRatingMap[v]