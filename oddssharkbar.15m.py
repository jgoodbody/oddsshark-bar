#!/usr/bin/python3

# <bitbar.title>OddsShark BitBar</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Joel Goodbody</bitbar.author>
# <bitbar.author.github>jgoodbody</bitbar.author.github>
# <bitbar.desc>Displays OddsShark Info</bitbar.desc>
# <bitbar.image>https://www.bigonsports.com/wp-content/uploads/2016/10/sports-betting-odds-explained.jpg</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/jgoodbody/oddsshark-bar</bitbar.abouturl>

# <xbar.var>select(VAR_FUTUREODDS="Bovada"): How to sort future odds? [Team, Opening, Bovada, BetOnline, SportsBetting]</xbar.var>

import os
import requests
import collections
from bs4 import BeautifulSoup

# For monospaced font
font = '| font=Courier | size=14'

site = 'https://www.oddsshark.com'
lgs = collections.defaultdict(dict)
lgs['UFC']['odds'] = requests.get(
    'https://io.oddsshark.com/ticker/ufc',
    headers = {
        'referer': site
    }
)

for league, active in lgs['UFC']['odds'].json()['leagues'].items():
    lgs[league.upper()]['futures'] = BeautifulSoup(requests.get(f"{site}/{league}/odds/futures").content, 'html.parser')
    if active==True:
        lgs[league.upper()]['odds'] = requests.get(
            'https://io.oddsshark.com/ticker/' + league, 
            headers = {
                'referer': site
            }
        ).json()['matchups']


class Future_Odds:
    def __init__(self, future, team, opening, bovada, betonline, sportsbetting):
        self.future = future
        self.team = team
        self.opening = opening
        self.bovada = bovada
        self.betonline = betonline
        self.sportsbetting = sportsbetting
    def __repr__(self):
        return repr((self.future, self.team, self.opening, self.bovada, self.betonline, self.sportsbetting))


def sorting_provider(x, provider):
    odd = getattr(x, provider)
    if odd == '':
        return float('inf')
    else:
        return int(odd)


def simple_odds(odds):
    for game in odds:
        if game['type'] == 'date':
            print('--', game['date']['fullday'], game['date']['month'], game['date']['day'])
        if game["type"] == "matchup":
            if 'matchup_link' in game:
                print('----', game['status'], font, '| href=' + site + game['matchup_link'])
            else:
                print('----', game['status'], font)
            if game['status'].startswith('FINAL'):
                print('----', game['away_short_name'], game['away_score'], font)
                print('----', game['home_short_name'], game['home_score'], font)
            else:
                print('----', game['away_short_name'], game['away_odds'] if game['away_odds'].startswith('-') else '+' + game['away_odds'], font)
                print('----', game['home_short_name'], game['home_odds'] if game['home_odds'].startswith('-') else '+' + game['home_odds'], font)


def ufc_odds(odds):
    print('UFC')
    for fight in odds:
        if fight['type'] == 'event':
            print('--', fight['event'])
        if fight["type"] == 'matchup':
            if not fight['status']:
                print('----', fight['event_date'][11:])
                print('----', fight['away_name'], fight['away_odds'] if fight['away_odds'].startswith('-') else '+' + fight['away_odds'], '| font=Courier')
                print('----', fight['home_name'], fight['home_odds'] if fight['home_odds'].startswith('-') else '+' + fight['home_odds'], '| font=Courier')
            else:
                print('----', 'FINAL')
                print('----', fight['away_name'], fight['status'] if fight['away_name'] == fight['winner'] else '', '| font=Courier')
                print('----', fight['home_name'], fight['status'] if fight['home_name'] == fight['winner'] else '', '| font=Courier')


def process_odds_section(soup, html_type, html_class):
    data = soup.find_all(html_type, class_=html_class)
    init_list = []
    daysofweek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
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
            rows.append(Future_Odds(future, team,
                         opening[odds_inc],
                         futures_trios[odds_inc][0],
                         futures_trios[odds_inc][1],
                         futures_trios[odds_inc][2]))
            odds_inc += 1
        else:
            rows.append([team])
            future = team
    return rows


def print_all_odds(lgs):
    for sport in lgs:
        if sport not in ['UFC','SOCCER']:
            print(sport)
            if 'odds' in lgs[sport]:
                simple_odds(lgs[sport]['odds'])
            print('-- Futures')
        elif sport == 'UFC':
            ufc_odds(lgs[sport]['odds'])
        opening_odds = process_odds_section(lgs[sport]['futures'], 'div', ['op-item op-future-item', 'op-item op-future-item '])
        current_odds = process_odds_section(lgs[sport]['futures'], 'div', 'op-item op-future-item no-vegas')
        team_list = process_odds_section(lgs[sport]['futures'], ['div','span'], ['align-bottom',
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
            if type(odds) is list:
                print('----', odds[0], font)
                print('------ {0:<21}{1:>8}{2:>8}{3:>14}{4:>15}{5}'.format('Team','Opening','Bovada','BetOnline.AG','Sports Betting',font))
                futures = [fut for fut in all_odds if hasattr(fut, 'future') and fut.future == odds[0]]
                futures = sorted(futures, key=lambda x: sorting_provider(x, os.environ.get('VAR_FUTUREODDS').lower()))
                for odds in futures:
                    print('------ {0:<21}{1:>8}{2:>8}{3:>14}{4:>15}{5}'.format(odds.team, odds.opening, odds.bovada, odds.betonline, odds.sportsbetting, font))


print('OddsShark Bar')
print('---')
print_all_odds(lgs)
