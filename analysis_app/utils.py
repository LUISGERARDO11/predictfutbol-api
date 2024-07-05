import requests
import json
import logging

API_TOKEN = 'e4126365396e46f38ce24d39ed898c98'
base_url = 'https://api.football-data.org/v4'
headers = {
    'X-Auth-Token': API_TOKEN
}

logger = logging.getLogger(__name__)

TEAMS_DATA = {}


def fetch_teams_data(competition_id='PL'):
    global TEAMS_DATA
    logger.info('Ejecutando fetch_teams_data...')  # Mensaje de depuración al inicio de la función
    next_match = get_next_match(competition_id)
    teams = get_teams_from_next_match(next_match)
    TEAMS_DATA = teams
    logger.info('Datos de equipos obtenidos: %s', TEAMS_DATA)  # Mensaje de depuración después de obtener los datos

def get_next_match(competition_id='PL'):
    try:
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?status=SCHEDULED', headers=headers)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        if matches:
            next_match = matches[0]
            return next_match
        else:
            return None
    except requests.RequestException as e:
        logger.error(f'Error al obtener los partidos: {e}')
        return None

def get_teams_from_next_match(match):
    if match:
        return {
            'homeTeam': match['homeTeam']['shortName'],
            'awayTeam': match['awayTeam']['shortName']
        }
    return {}
