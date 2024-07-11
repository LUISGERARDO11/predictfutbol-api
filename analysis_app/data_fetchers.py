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

def get_teams_next_season(competition_id='PL', season='2024'):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/teams?season={season}', headers=headers)
        response.raise_for_status()
        teams_data = response.json()

        teams = []
        if 'teams' in teams_data:
            for team in teams_data['teams']:
                teams.append(team['shortName'])
        else:
            raise Exception('No se encontraron equipos en la respuesta.')

        teams.sort()
        return teams
    except requests.RequestException as e:
        print(f'Error al obtener los equipos de la próxima temporada: {e}')
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None

def get_scheduled_matches(competition_id='PL', season='2024'):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?season={season}', headers=headers)
        response.raise_for_status()
        matches_data = response.json()

        matches_by_matchday = {}
        if 'matches' in matches_data:
            for match in matches_data['matches']:
                match_info = {
                    'utcDate': match['utcDate'],
                    'homeTeam': match['homeTeam']['shortName'],
                    'awayTeam': match['awayTeam']['shortName'],
                    'status': match['status']
                }
                matchday = match['matchday']
                if matchday not in matches_by_matchday:
                    matches_by_matchday[matchday] = []
                matches_by_matchday[matchday].append(match_info)
        else:
            raise Exception('No se encontraron partidos en la respuesta.')

        for matchday in matches_by_matchday:
            matches_by_matchday[matchday].sort(key=lambda x: datetime.strptime(x['utcDate'], '%Y-%m-%dT%H:%M:%SZ'))

        sorted_matchdays = sorted(matches_by_matchday.items())
        ordered_matches = [{"matchday": md, "matches": matches} for md, matches in sorted_matchdays]

        return ordered_matches
    except requests.RequestException as e:
        print(f'Error al obtener los partidos programados: {e}')
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None
