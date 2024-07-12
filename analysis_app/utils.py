import requests
import logging
import time
from datetime import datetime

API_TOKEN = 'cc61b4c3b231421781f1a030f9a1d213'
base_url = 'https://api.football-data.org/v4'
headers = {
    'X-Auth-Token': API_TOKEN
}

logger = logging.getLogger(__name__)

def fetch_teams_data(competition_id='PL'):
    logger.info('Ejecutando fetch_teams_data...')
    next_match = get_next_match(competition_id)
    if next_match is None:
        logger.error('No se pudo obtener el siguiente partido.')
        return None
    teams = get_teams_from_next_match(next_match)
    logger.info('Datos de equipos obtenidos: %s', teams)
    return teams


def get_next_match(competition_id='PL', retry_count=0):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?status=SCHEDULED', headers=headers)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        if matches:
            next_match = matches[0]
            return next_match
        else:
            return None
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            retry_count += 1
            delay = min(60 * (2 ** retry_count), 3600)
            logger.error(f'Rate limit exceeded. Retrying after {delay} seconds...')
            time.sleep(delay)
            return get_next_match(competition_id, retry_count)
        else:
            logger.error(f'Error al obtener los partidos: {e}')
            return None

def get_teams_from_next_match(match):
    if match:
        return {
            'homeTeam': match['homeTeam']['shortName'],
            'awayTeam': match['awayTeam']['shortName']
        }
    return {}

def get_teams_next_season(competition_id='PL', season='2024', max_retries=3, backoff_factor=2):
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(
                f'{base_url}/competitions/{competition_id}/teams?season={season}',
                headers=headers,
                timeout=10  # Aumentar el tiempo de espera a 10 segundos
            )
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
            attempt += 1
            print(f'Error al obtener los equipos de la próxima temporada: {e}. Intento {attempt} de {max_retries}.')
            time.sleep(backoff_factor ** attempt)  # Incrementar el tiempo de espera exponencialmente

        except Exception as e:
            print(f'Error: {e}')
            return None

    print('Se agotaron todos los intentos para obtener los equipos de la próxima temporada.')
    return None

    
def get_scheduled_matches(competition_id='PL', season='2024', max_retries=3, backoff_factor=2):
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(
                f'{base_url}/competitions/{competition_id}/matches?season={season}',
                headers=headers,
                timeout=10  # Aumentar el tiempo de espera a 10 segundos
            )
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
            attempt += 1
            print(f'Error al obtener los partidos programados: {e}. Intento {attempt} de {max_retries}.')
            time.sleep(backoff_factor ** attempt)  # Incrementar el tiempo de espera exponencialmente

        except Exception as e:
            print(f'Error: {e}')
            return None

    print('Se agotaron todos los intentos para obtener los partidos programados.')
    return None
