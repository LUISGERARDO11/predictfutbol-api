# analysis_app/utils.py

from django.core.cache import cache
import requests
import logging
import time

API_TOKEN = 'e4126365396e46f38ce24d39ed898c98'
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
        return
    teams = get_teams_from_next_match(next_match)
    cache.set('TEAMS_DATA', teams, timeout=None)
    logger.info('Datos de equipos obtenidos: %s', teams)

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

        teams2 = teams.sort()

        # Guardar los datos en caché
        cache.set('TEAMS_NEXT_SEASON', teams2, timeout=None)  # Cache for one week

        return teams2

    except requests.RequestException as e:
        print(f'Error al obtener los equipos de la próxima temporada: {e}')
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None
