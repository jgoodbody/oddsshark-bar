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
from bs4 import BeautifulSoup

#For monospaced font
font = '| font=Courier'

site = 'https://www.oddsshark.com'

lg_tks = {}
lg_futs = {}
lg_tks['UFC'] = requests.get(
    'https://io.oddsshark.com/ticker/ufc', 
    headers = {
        'referer': site
    }
)

for league, active in lg_tks['UFC'].json()['leagues'].items():
    lg_futs[league.upper()] = BeautifulSoup(requests.get(f"{site}/{league}/odds/futures").content, 'html.parser')
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


def process_odds_section(soup, html_type, html_class):
    data = soup.find_all(html_type, class_=html_class)
    init_list = []
    daysofweek = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for elem in data:
        if not elem.get_text().startswith(tuple(daysofweek)):
            init_list.append(elem.get_text().strip())
    return init_list

def create_futures_data(teams, opening, currents):
    
    futures_trios = []
    for a, b, c in zip(*[iter(currents)]*3):
        futures_trios.append([a,b,c])
    
    rows = []
    odds_inc = 0
    sports = ['MLB','NFL','NHL','NBA','College Basketball','College Football']
    for team in teams:
        if not team.startswith(tuple(sports)):
            rows.append([team,
                         opening[odds_inc],
                         futures_trios[odds_inc][0],
                         futures_trios[odds_inc][1],
                         futures_trios[odds_inc][2]])
            odds_inc += 1
        else:
            rows.append([team])
    return rows


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
print('Futures Test')
print('---')    
for sport in lg_futs:
    print(sport)
    opening_odds = process_odds_section(lg_futs[sport], 'div', 'op-item op-future-item ')
    current_odds = process_odds_section(lg_futs[sport], 'div', 'op-item op-future-item no-vegas')
    team_list = process_odds_section(lg_futs[sport], ['div','span'], ['align-bottom',
                                                                      'op-team baseball op-odd',
                                                                      'op-team baseball op-even',
                                                                      'op-team basketball op-odd',
                                                                      'op-team basketball op-even',
                                                                      'op-team football op-odd',
                                                                      'op-team football op-even',
                                                                      'op-team hockey op-odd',
                                                                      'op-team hockey op-even'])
    all_odds = create_futures_data(team_list, opening_odds, current_odds)
    for odds in all_odds:
        if len(odds) > 1:
            print('----', odds[0], odds[1], odds[2], odds[3], odds[4])
        else:
            print('--', odds[0])
            print('----', 'Opening', 'Bovada', 'BetOnline.AG', 'Sports Betting')