#!/usr/bin/python3

# <bitbar.title>OddsShark BitBar</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Joel Goodbody</bitbar.author>
# <bitbar.author.github>jgoodbody</bitbar.author.github>
# <bitbar.desc>Displays OddsShark Info</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/jgoodbody/oddsshark-bar</bitbar.abouturl>

import requests

lg_tks = {}
lg_tks['UFC'] = requests.get(
    'https://io.oddsshark.com/ticker/ufc', 
    headers = {
        'referer': 'https://www.oddsshark.com/'
    }
)

for league, active in lg_tks['UFC'].json()['leagues'].items():
    if active==True:
        lg_tks[league.upper()] = requests.get(
            'https://io.oddsshark.com/ticker/' + league, 
            headers = {
                'referer': 'https://www.oddsshark.com/'
            }
        ).json()['matchups']

def simple_odds(odds):
    for game in odds:
        if game["type"] == "matchup":
            print('--',game['away_short_name'],game['away_odds'], game['status'])
            print('--',game['home_short_name'],game['home_odds'])        

print('OddsShark Bar')
print('---')
for sport, odds in lg_tks.items():
    if sport != 'UFC':
        print(sport)
        simple_odds(odds)
        print('---')
print('UFC')
for fight in lg_tks['UFC']:
    if fight["type"] == 'matchup':
        print('----', fight['away_name'], fight['away_odds'], fight['status'])
        print('----', fight['home_name'], fight['home_odds'])
    if fight['type'] == 'event':
        print('--', fight['event'])