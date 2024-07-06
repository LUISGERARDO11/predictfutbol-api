from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from .predictor import predict
from .utils import TEAMS_DATA
import requests

API_TOKEN = 'cc61b4c3b231421781f1a030f9a1d213'
base_url = 'https://api.football-data.org/v4'
headers = {
    'X-Auth-Token': API_TOKEN
}

def get_external_data(competition_id='PL'):
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
                'group': next_match['group'],
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


def make_prediction_logic():
    if not TEAMS_DATA:
        raise Exception('No se encontraron datos de equipos.')
    
    home_team = TEAMS_DATA['homeTeam']
    away_team = TEAMS_DATA['awayTeam']
    
    # Prepara los datos de entrada para la predicción
    input_data = {'HomeTeam': home_team, 'AwayTeam': away_team}
    
    # Hacer la predicción
    prediction = predict(input_data)
    return prediction

def make_prediction_logic_without_teamdata(home_team_name, away_team_name):
    # Prepara los datos de entrada para la predicción
    input_data = {'HomeTeam': home_team_name, 'AwayTeam': away_team_name}
    
    # Hacer la predicción
    prediction = predict(input_data)  # Asume que predict está implementada correctamente
    return prediction

def get_team_by_shortname(short_name, competition_id='PL'):
    try:
        # Realizar la solicitud GET a la API
        response = requests.get(f'{base_url}/competitions/{competition_id}/teams', headers={'X-Auth-Token': API_TOKEN})
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        data = response.json()

        # Buscar el equipo por nombre corto
        for team in data['teams']:
            if team['shortName'] == short_name:
                team_info = {
                    'crestUrl': team['crest']
                }
                return team_info
        
        return None  # Retorna None si no se encuentra el equipo con el nombre corto dado
    
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
    
@api_view(['GET'])
def make_prediction(request):
    try:
        prediction = make_prediction_logic()
        additional_data = get_external_data()
        # Construir el JSON de respuesta
        result = {
            'prediction': prediction,
            'additional_data': additional_data,
        }
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['POST'])
def make_prediction_without_teamdata(request: HttpRequest):
    try:
        # Obtener los nombres de los equipos desde los parámetros POST
        home_team_name = request.data.get('homeTeam')
        away_team_name = request.data.get('awayTeam')
        
        # Obtener logos de los equipos
        home_team_logo = get_team_by_shortname(home_team_name)
        away_team_logo = get_team_by_shortname(away_team_name)
        
        # Hacer la predicción basada en los nombres de los equipos
        prediction = make_prediction_logic_without_teamdata(home_team_name, away_team_name)
        
        # Construir el JSON de respuesta
        result = {
            'prediction': prediction,
            'homeTeamLogo': home_team_logo,
            'awayTeamLogo': away_team_logo
        }
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
def get_teams_season(request):
    teams = get_teams_next_season()
    if teams:
        return JsonResponse({'teams': teams})
    else:
        return JsonResponse({'error': 'No se pudieron obtener los equipos de la próxima temporada.'}, status=500)
    
@api_view(['GET'])
def welcome_view(request):
    return JsonResponse({'message': 'Hola mundo'})
