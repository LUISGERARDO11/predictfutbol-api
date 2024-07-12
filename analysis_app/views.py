# analysis_app/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from .predictor import predict
from django.core.cache import cache
import requests
import logging

API_TOKEN = 'cc61b4c3b231421781f1a030f9a1d213'
base_url = 'https://api.football-data.org/v4'
headers = {
    'X-Auth-Token': API_TOKEN
}

logger = logging.getLogger(__name__)

def get_external_data(competition_id='PL'):
    """
    Obtiene detalles específicos del próximo partido programado para una competencia específica.

    Args:
        competition_id (str): ID de la competencia (por defecto 'PL' para Premier League).

    Returns:
        dict or None: Detalles específicos del próximo partido o None si no se encuentra.
    """
    try:
        # Filtrar partidos por la fecha actual y futura
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?status=SCHEDULED', headers=headers)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        
        if matches:
            next_match = matches[0]  # El primer partido en la lista es el próximo
            
            # Extraer los campos específicos requeridos
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
            logger.warning('No se encontraron partidos programados.')
            return None
    except requests.RequestException as e:
        logger.error(f'Error al obtener los detalles del próximo partido: {e}')
        return None


def make_prediction_logic():
    teams_data = cache.get('TEAMS_DATA')
    if not teams_data:
        raise Exception('No se encontraron datos de equipos.')
    
    home_team = teams_data['homeTeam']
    away_team = teams_data['awayTeam']
    
    # Prepara los datos de entrada para la predicción
    input_data = {'HomeTeam': home_team, 'AwayTeam': away_team}
    
    # Hacer la predicción
    prediction = predict(input_data)
    return prediction

@api_view(['GET'])
def make_prediction(request):
    try:
        prediction = make_prediction_logic()
        additional_data = get_external_data()
        
        # Construir el JSON de respuesta
        result = {
            'prediction': prediction,
            'additional_data': additional_data
        }
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f'Error en la predicción: {e}')
        return JsonResponse({'error': str(e)}, status=500)

def make_prediction_logic_without_teamdata(home_team_name, away_team_name):
    # Prepara los datos de entrada para la predicción
    input_data = {'HomeTeam': home_team_name, 'AwayTeam': away_team_name}
    
    # Hacer la predicción
    prediction = predict(input_data)  # Asume que predict está implementada correctamente
    return prediction

@api_view(['POST'])
def make_prediction_without_teamdata(request: HttpRequest):
    try:
        # Obtener los nombres de los equipos desde los parámetros POST
        home_team_name = request.data.get('homeTeam')
        away_team_name = request.data.get('awayTeam')
        
        # Hacer la predicción basada en los nombres de los equipos
        prediction = make_prediction_logic_without_teamdata(home_team_name, away_team_name)
        
        # Construir el JSON de respuesta
        result = {
            'prediction': prediction
        }
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f'Error en la predicción sin datos del equipo: {e}')
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def welcome_view(request):
    return JsonResponse({'message': 'Hola mundo'})

@api_view(['GET'])
def get_teams_season(request):
    teams_next_season = cache.get('TEAMS_NEXT_SEASON')
    return JsonResponse({'teams': teams_next_season})