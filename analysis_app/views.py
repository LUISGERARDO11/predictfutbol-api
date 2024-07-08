from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from .predictor import predict, retrain_model_logic
from .utils import TEAMS_DATA
import requests
import pandas as pd
from datetime import datetime

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

def get_scheduled_matches(competition_id='PL', season='2024'):
    try:
        # Realizar la solicitud GET a la API para obtener los partidos de la temporada especificada
        response = requests.get(f'{base_url}/competitions/{competition_id}/matches?season={season}', headers=headers)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        matches_data = response.json()

        # Crear un diccionario para organizar los partidos por jornada
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

        # Ordenar los partidos dentro de cada jornada por fecha
        for matchday in matches_by_matchday:
            matches_by_matchday[matchday].sort(key=lambda x: datetime.strptime(x['utcDate'], '%Y-%m-%dT%H:%M:%SZ'))

        # Convertir el diccionario a una lista de jornadas ordenadas
        sorted_matchdays = sorted(matches_by_matchday.items())
        ordered_matches = [{"matchday": md, "matches": matches} for md, matches in sorted_matchdays]

        return ordered_matches

    except requests.RequestException as e:
        print(f'Error al obtener los partidos programados: {e}')
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

@api_view(['GET'])
def get_matches_scheduled(request):
    matches = get_scheduled_matches()
    if matches:
        return JsonResponse(matches, safe=False)
    else:
        return JsonResponse({'error': 'No se pudieron obtener los partidos programados para la temporada 2024-2025 de la Premier League.'}, status=500)

@api_view(['POST'])
def retrain_model(request):
    required_columns = ['AwayTeam', 'HF', 'AC', 'AR', 'FTAG', 'HST', 'HY', 'FTHG', 'HS', 'AF', 'AY', 'AS', 'AST', 'HomeTeam', 'HC']

    try:
        # Verificar si el archivo está en los archivos de la solicitud
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No se ha proporcionado ningún archivo.'}, status=400)

        # Leer el archivo CSV
        file = request.FILES['file']
        df = pd.read_csv(file)

        # Verificar si todas las columnas requeridas están presentes
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({'error': f'Faltan las siguientes columnas requeridas: {", ".join(missing_columns)}'}, status=400)

         # Llamada a la lógica de reentrenamiento
        result = retrain_model_logic(df)

        return JsonResponse({'message': 'Archivo leído correctamente. ' + result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
