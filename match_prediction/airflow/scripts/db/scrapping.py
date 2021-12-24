from match_prediction.airflow.scripts.get_logger import get_logger
from datetime import datetime
from logging import log
import requests
import os


teams_map = {
    'Arsenal FC': 'arsenal',
    'Aston Villa FC': 'aston-villa',
    'Brentford FC': 'brentford',
    'Brighton & Hove Albion FC': 'brighton',
    'Burnley FC': 'burnley', 
    'Chelsea FC': 'chelsea', 
    'Crystal Palace FC': 'crystal-palace',
    'Everton FC': 'everton',
    'Leeds United FC': 'leeds',
    'Leicester City FC': 'leicester',
    'Liverpool FC': 'liverpool',
    'Manchester City FC': 'manchester-city',
    'Manchester United FC': 'manchester-utd',
    'Norwich City FC': 'norwich', 
    'Newcastle United FC': 'newcastle',
    'Southampton FC': 'southampton', 
    'Tottenham Hotspur FC': 'tottenham',
    'Watford FC': 'watford',
    'West Ham United FC': 'west-ham',
    'Wolverhampton Wanderers FC': 'wolverhampton'
}

def parse_match(match_stats: dict, match: dict):
    match_stats['winner'] = match['score']['winner']
    match_stats['fthg'] = match['score']['fullTime']['homeTeam']
    match_stats['ftag'] = match['score']['fullTime']['awayTeam']
    match_stats['hthg'] = match['score']['halfTime']['homeTeam']
    match_stats['htag'] = match['score']['halfTime']['awayTeam']

    match_stats['home_team'] = teams_map[match['homeTeam']['name']]
    match_stats['away_team'] = teams_map[match['awayTeam']['name']]
    
    match_stats['status'] = match['status']
    match_stats['match_date'] = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
    
    if len(match['referees']):
        match_stats['referee'] = match['referees'][0]['name']
    else:
        match_stats['referee'] = None

def parse_json(json_file):
    match_stats = [dict() for _ in range(json_file['count'])]
    matches = json_file['matches']

    for i, match in enumerate(matches):
        parse_match(match_stats[i], match)
    return match_stats

def get_all_matches_stats():
    logger = get_logger(__file__)

    try:
        api_token = os.environ['API_TOKEN']
        request = 'https://api.football-data.org/v2/competitions/PL/matches'

        response = requests.get(
            request,
            headers={'X-Auth-Token': api_token}
        ).json()
        res = parse_json(response)
    except Exception as e:
        logger.exception(e)
    return res

#print(get_all_matches_stats()[0])