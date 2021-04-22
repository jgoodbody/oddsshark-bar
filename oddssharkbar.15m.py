#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

# <bitbar.title>OddsShark BitBar</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Joel Goodbody</bitbar.author>
# <bitbar.author.github>jgoodbody</bitbar.author.github>
# <bitbar.desc>Displays OddsShark Info</bitbar.desc>
# <bitbar.image>https://www.bigonsports.com/wp-content/uploads/2016/10/sports-betting-odds-explained.jpg</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/jgoodbody/oddsshark-bar</bitbar.abouturl>

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
    for a, b, c in zip(*[iter(currents)] * 3):
        futures_trios.append([a, b, c])

    rows = []
    odds_inc = 0
    sports = ['MLB', 'NFL', 'NHL', 'NBA', 'College Basketball', 'College Football']
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


def print_all_odds(lgs):
    for sport in lgs:
        print(sport)
        if sport != 'UFC':
            if 'odds' in lgs[sport]:
                simple_odds(lgs[sport]['odds'])
        else:
            for fight in lgs['UFC']['odds']:
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
        if 'futures' in lgs[sport]:
            print('-- Futures')
        for odds in all_odds:
            if len(odds) > 1:
                print('------ {0:<21}{1:>8}{2:>8}{3:>14}{4:>15}{5}'.format(odds[0], odds[1], odds[2], odds[3], odds[4], font))
            else:
                print('----', odds[0], font)
                print('------ {0:<21}{1:>8}{2:>8}{3:>14}{4:>15}{5}'.format('Team','Opening','Bovada','BetOnline.AG','Sports Betting',font))


print('OddsShark Bar')
print('---')
print_all_odds(lgs)
