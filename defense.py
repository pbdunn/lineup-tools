#!/usr/bin/env python

import itertools
import math
import random

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_players():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1rYfknccqzbA_hI2lpq7NoabSCHlS3fr9QY6pDfD2Eho'
    rangeName = 'Defense!B2:N14'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    if not values:
        print "No data found"
    else:
        players = {}
        for row in values:
            player = str(row.pop(0))
            players[player] = []
            for innings in row:
                players[player].append(int(innings))
    return players

def prune_players(players):
    for player in players.keys():
        answer = str(raw_input("Include {} [y/n]? ".format(player))).lower().strip()
        if not answer[0] == 'y':
            del players[player]
    return players

def configure_lineup(numplayers):
    if numplayers == 13:
        return [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 11, 11]
    elif numplayers == 12:
        return [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 11]
    elif numplayers == 11:
        return [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11]
    elif numplayers == 10:
        return [0, 1, 2, 3, 4, 5, 6, 7, 9, 10]
    elif numplayers == 9:
        return [0, 1, 2, 3, 4, 5, 6, 8, 10]
    elif numplayers == 8:
        return [0, 1, 2, 3, 4, 5, 7, 9]
    elif numplayers == 7:
        return [0, 1, 2, 3, 4, 5, 8]
    elif numplayers == 6:
        return [0, 1, 2, 3, 4, 5]

def update_players(players, bestlineup, lineupconfig):
    for i, player in enumerate(bestlineup):
        pos = lineupconfig[i]
        players[player][pos] = float('inf')
    return players

def main():
    players = get_players()
    players = prune_players(players)
    numplayers = len(players)
    lineupconfig = configure_lineup(numplayers)
    numlineups = int(raw_input("How many lineups? ").strip())
    lineups = []
    innings = [0 for i in range(numplayers)]
    for inning in range(numlineups):
        bestsum = float('inf')
        bestmax = float('inf')
        print "Processing {:,} lineups of {} players: ".format(math.factorial(len(players)), len(players)) + str(players.keys())
        for curlineup in itertools.permutations(players):
            for i, player in enumerate(curlineup):
                pos = lineupconfig[i]
                innings[i] = players[player][pos]
            cursum = sum(innings)
            curmax = max(innings)
            if cursum > bestsum:
                continue
            elif cursum == bestsum:
                if curmax > bestmax:
                    continue
                elif curmax == bestmax:
                    if random.randint(0, 1):
                        continue
            bestsum = cursum
            bestmax = curmax
            bestlineup = curlineup
            print "New Best Lineup: " + str(bestlineup) + " Sum: " + str(bestsum) + " Max: " + str(bestmax)
        lineups.append(bestlineup)
        players = update_players(players, bestlineup, lineupconfig)
    for lineup in lineups:
        print str(lineup)

if __name__ == '__main__':
    main()
