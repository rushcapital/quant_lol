from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import pickle
import string
import multiprocessing

def query_league_match_history(league, headers):

    response = requests.get(f'https://gol.gg/tournament/tournament-matchlist/{league}%20Summer%202022/', headers=headers).text
    match_history = pd.read_html(response).pop()
    return match_history

def get_team_ids(league, headers, base, mappings):
    
    mapping  = mappings[league]
    response = requests.get(f'https://gol.gg/tournament/tournament-ranking/{league}%20Summer%202022/', headers=headers).text
    soup     = BeautifulSoup(response, 'html.parser')
    table    = soup.findAll('table')[0]
    links    = table.findAll('a')
    storage  = {mapping[link.text]:{'team_page':base + link.get('href').split('..')[-1]} for link in links}
    
    return storage

def get_match_history(team_pages, headers, base, mappings):

    for team, team_dict in team_pages.items(): 
        first_no = re.compile(r'\d+')
        first_no = first_no.search(team_dict['team_page']).group()
        response = requests.get(f'https://gol.gg/teams/team-matchlist/{first_no}/split-Summer/tournament-ALL/', headers=headers).text
        soup     = BeautifulSoup(response, 'html.parser')
        table    = soup.findAll('table')[1]
        rows     = table.findAll('tr')
        
        storage  = {}

        for row in rows[1:]:
            cols    = row.findAll('td')
            cols    = [ele.text.strip() for ele in cols]
            
            # get match result.
            result  = cols[0]

            # get kills / patch / opponent
            kills   = cols[3]
            patch   = cols[-3]
            opp     = cols[7]

            week    = cols[-2][-1]
            
            href    = [match.get('href') for match in row.findAll('a') if 'game' in match.get('href')][0]
            href    = base + href.split('../')[-1]

            alph    = list(string.ascii_lowercase)
            incr    = 0
            while week in storage:
                week = week + alph[incr]
                incr += 1
                
            
            storage[week] = {
                'team'  : team,
                'result': result,
                'kills' : kills,
                'patch' : patch,
                'opp'   : opp,
                'href'  : href
            }

            incr = 0
            
        team_pages[team]['match_history'] = storage 

    return team_pages

def gather_match_data(tup):
	    
    _dic = tup[1]
    _dic['game'] = tup[0]
    headers = tup[2]

    attempts = 0
    while True:
        try:
            response = requests.get(_dic['href'], headers=headers).text
            # soup     = BeautifulSoup(response, 'html.parser')	
            tables   = pd.read_html(response)
            kdas     = [df.loc[:, ~df.columns.str.contains('^Unnamed')] for df in tables if 'Player' in df.columns]
            gold_dmg = [df for df in tables if _dic['team'] in list(df.iloc[0])]

            gold = gold_dmg[0]
            dmg  = gold_dmg[1]

            team_a = gold.iloc[0][1]
            team_b = gold.iloc[0][2]
            _idx   = None

            if team_a == _dic['team']:
                _idx = 0 
            else:
                _idx = 1

            gold = gold[1:]
            dmg  = dmg[1:]

            players = {}
            _team   = kdas[_idx]

            for _, row in _team.iterrows():
                players[row['Player']] = {
                    'k': int(row['KDA'].split('/')[0]),
                    'd': int(row['KDA'].split('/')[1]),
                    'a': int(row['KDA'].split('/')[2])
                }

            keys = list(players.keys())
            
            for idx, row in gold.iterrows():	
                players[keys[idx-1]]['gold'] = round(float(list(row)[_idx+1].replace("%",""))/100,3)

            for idx, row in dmg.iterrows():
                players[keys[idx-1]]['dmg'] = round(float(list(row)[_idx+1].replace("%",""))/100,3)

            _dic['players'] = players           
            
            print('completed:', _dic['team'], tup[0])
            break
        
        except Exception as err:
            print(err)
            print(_dic['team'],_dic['game'],':', _dic['href'],'. retrying. attempt:', attempts)
            attempts += 1

    return _dic


if __name__ == '__main__':

    mappings = {
        'LPL':  {
            'Victory Five'       : 'V5',
            'Top Esports'        : 'TOP',
            'JD Gaming'          : 'JDG',
            'Royal Never Give Up': 'RNG',
            'Edward Gaming'      : 'EDG',
            'Weibo Gaming'       : 'WBG',
            'OMG'                : 'OMG',
            'LNG Esports'        : 'LNG',
            'Anyone s Legend'    : 'AL',
            'Bilibili Gaming'    : 'BLG',
            'Funplus Phoenix'    : 'FPX',
            'LGD Gaming'         : 'LGD',
            'Rare Atom'          : 'RA',
            'Ultra Prime'        : 'UP',
            'Team WE'            : 'WE',
            'TT'                 : 'TT',
            'Invictus Gaming'    : 'IG'
        },
        'LCK':  {
            'Gen.G eSports'      : 'GEN',
            'T1'                 : 'T1',
            'Liiv SANDBOX'       : 'LSB',
            'DWG KIA'            : 'DWG',
            'KT Rolster'         : 'KT',
            'DRX'                : 'DRX',
            'Kwangdong Freecs'   : 'KDF',
            'Fredit BRION'       : 'BRO',
            'Nongshim RedForce'  : 'NS',
            'Hanwha Life eSports': 'HLE',
        }
    }

    BASE_URL = 'https://gol.gg/'
    HEADERS  = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    
    team_pages = get_team_ids('LPL', HEADERS, BASE_URL, mappings)
    
    t = get_match_history(team_pages, HEADERS, BASE_URL, mappings)
    
    with open('../datasets/match_history.pkl', 'wb') as handle:
        pickle.dump(t, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('../datasets/match_history.pkl', 'rb') as handle:
        pkl = pickle.load(handle)
    
    tups = []
    for team, team_dict in pkl.items():
        for k,v in team_dict['match_history'].items():
            tups.append((k, v, HEADERS))

    with multiprocessing.Pool(6) as pool:
        results = pool.map(gather_match_data, tups)

    with open('../datasets/lpl_stats.pkl', 'wb') as handle:
        pickle.dump(t, handle, protocol=pickle.HIGHEST_PROTOCOL)