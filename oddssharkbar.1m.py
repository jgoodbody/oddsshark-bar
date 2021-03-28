#!/usr/bin/python3

# <bitbar.title>OddsShark BitBar</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Joel Goodbody</bitbar.author>
# <bitbar.author.github>jgoodbody</bitbar.author.github>
# <bitbar.desc>Displays OddsShark Info</bitbar.desc>
# <bitbar.image>https://www.bigonsports.com/wp-content/uploads/2016/10/sports-betting-odds-explained.jpg</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/jgoodbody/oddsshark-bar</bitbar.abouturl>

import requests

#For monospaced font
font = '| font=Courier'

site = 'https://www.oddsshark.com'

lg_tks = {}
lg_tks['UFC'] = requests.get(
    'https://io.oddsshark.com/ticker/ufc', 
    headers = {
        'referer': site
    }
)

for league, active in lg_tks['UFC'].json()['leagues'].items():
    if active==True:
        lg_tks[league.upper()] = requests.get(
            'https://io.oddsshark.com/ticker/' + league, 
            headers = {
                'referer': site
            }
        ).json()['matchups']


def simple_odds(odds):
    for game in odds:
        if game['type'] == 'date':
            print('--', game['date']['fullday'], game['date']['month'], game['date']['day'])
        if game["type"] == "matchup":
            print('----', game['status'], '| font=Courier | href=' + site + game['matchup_link'])
            if game['status'].startswith('FINAL'):
                print('----', game['away_short_name'], game['away_score'], font)
                print('----', game['home_short_name'], game['home_score'], font)
            else:
                print('----', game['away_short_name'], game['away_odds'] if game['away_odds'].startswith('-') else '+' + game['away_odds'], font)
                print('----', game['home_short_name'], game['home_odds'] if game['home_odds'].startswith('-') else '+' + game['home_odds'], font)


print('OddsShark Bar')
print('---')
for sport, odds in lg_tks.items():
    if sport != 'UFC':
        print(sport)
        simple_odds(odds)
        print('---')
print('UFC')
for fight in lg_tks['UFC']:
    if fight['type'] == 'event':
        print('--', fight['event'])
    if fight["type"] == 'matchup':
        if not fight['status']:
            print('----', fight['event_date'][11:])
            print('----', fight['away_name'], fight['away_odds'] if fight['away_odds'].startswith('-') else '+' + fight['away_odds'], font)
            print('----', fight['home_name'], fight['home_odds'] if fight['home_odds'].startswith('-') else '+' + fight['home_odds'], font)
        else:
            print('----', 'FINAL')
            print('----', fight['away_name'], fight['status'] if fight['away_name'] == fight['winner'] else '', font)
            print('----', fight['home_name'], fight['status'] if fight['home_name'] == fight['winner'] else '', font)