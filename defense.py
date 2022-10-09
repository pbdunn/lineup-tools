#!/usr/bin/env python3

import itertools
import math
import random
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1ZM7_0IXk5sfDY1YsTJSPVNJQWYV_H8gnjm7OwN3zAsc'
RANGE_NAME = 'Defense!B2:N13'

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_players():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print("No data found")
    else:
        players = {}
        for row in values:
            player = str(row.pop(0))
            players[player] = []
            for innings in row:
                players[player].append(int(innings))
    return players

def prune_players(players):
    for player in list(players.keys()):
        answer = str(input("Include {} [y/n]? ".format(player))).lower().strip()
        if not answer[0] == 'y':
            del players[player]
    return players

def configure_lineup(numplayers):
    if numplayers == 13:
        return [0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 11, 11, 11]
    elif numplayers == 12:
        return [0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 11, 11]
    elif numplayers == 11:
        return [0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 11]
    elif numplayers == 10:
        return [0, 1, 2, 3, 4, 5, 6, 8, 10, 11]
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
        if pos:
            players[player][pos] += 1
        else:
            players[player][pos] = float('inf')
    return players

def main():
    players = get_players()
    players = prune_players(players)
    numplayers = len(players)
    lineupconfig = configure_lineup(numplayers)
    numlineups = int(input("How many lineups? ").strip())
    lineups = []
    innings = [0 for i in range(numplayers)]
    for inning in range(numlineups):
        bestsum = float('inf')
        bestmax = float('inf')
        print("Processing {:,} lineups of {} players: ".format(math.factorial(len(players)), len(players)) + str(list(players.keys())))
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
            print("New Best Lineup: " + str(bestlineup) + " Sum: " + str(bestsum) + " Max: " + str(bestmax))
        lineups.append(bestlineup)
        players = update_players(players, bestlineup, lineupconfig)
    for lineup in lineups:
        print(str(lineup))

if __name__ == '__main__':
    main()
