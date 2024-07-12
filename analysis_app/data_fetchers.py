import requests
from datetime import datetime

API_TOKEN = 'cc61b4c3b231421781f1a030f9a1d213'
base_url = 'https://api.football-data.org/v4'
headers = {
    'X-Auth-Token': API_TOKEN
}

def get_external_data(competition_id='PL'):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?status=SCHEDULED', headers=headers)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        
        if matches:
            next_match = matches[0]
            match_details = {
                'matchday': next_match.get('matchday'),
                'stage': next_match.get('stage'),
                'group': next_match.get('group'),
                'utcDate': next_match['utcDate'],
                'homeTeam': {
                    'name': next_match['homeTeam']['name'],
                    'shortName': next_match['homeTeam']['shortName'],
                    'crest': next_match['homeTeam']['crest']
                },
                'awayTeam': {
                    'name': next_match['awayTeam']['name'],
                    'shortName': next_match['awayTeam']['shortName'],
                    'crest': next_match['awayTeam']['crest']
                }
            }
            return match_details
        else:
            return None
    except requests.RequestException as e:
        print(f'Error al obtener los detalles del próximo partido: {e}')
        return None

def get_team_by_shortname(short_name, competition_id='PL'):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/teams', headers={'X-Auth-Token': API_TOKEN})
        response.raise_for_status()
        data = response.json()

        for team in data['teams']:
            if team['shortName'] == short_name:
                team_info = {
                    'crestUrl': team['crest']
                }
                return team_info
        
        return None
    except requests.RequestException as e:
        print(f'Error al buscar el equipo por nombre corto: {e}')
        return None

