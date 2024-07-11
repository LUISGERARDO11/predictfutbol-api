from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from .predictor import retrain_model_logic
from .data_fetchers import get_external_data, get_team_by_shortname
from .prediction_logic import make_prediction_logic, make_prediction_logic_without_teamdata
import pandas as pd
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def make_prediction(request):

    try:
        prediction = make_prediction_logic()
        #additional_data = get_external_data()
        # Construir el JSON de respuesta
        result = {
            'prediction': prediction,
            'additional_data': "additional_data",
        }
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    

@api_view(['POST'])
def make_prediction_without_teamdata(request: HttpRequest):
    try:
        home_team_name = request.data.get('homeTeam')
        away_team_name = request.data.get('awayTeam')
        
        home_team_logo = get_team_by_shortname(home_team_name)
        away_team_logo = get_team_by_shortname(away_team_name)
        
        prediction = make_prediction_logic_without_teamdata(home_team_name, away_team_name)
        
        result = {
            'prediction': prediction,
            'homeTeamLogo': home_team_logo,
            'awayTeamLogo': away_team_logo
        }
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
   
@api_view(['GET'])
def welcome_view(request):
    return JsonResponse({'message': 'Hola mundo'})

@api_view(['GET'])
def get_teams_season(request):
    teams_next_season = cache.get('TEAMS_NEXT_SEASON')
    if teams_next_season:
        response_data = {'teams': teams_next_season}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'No se encontraron datos de equipos para la próxima temporada en la caché.'}, status=404)

@api_view(['GET'])
def get_matches_scheduled(request):
    scheduled_matches = cache.get('SCHEDULED_MATCHES')
    if scheduled_matches:
        response_data = {'matches': scheduled_matches}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'No se encontraron partidos programados en la caché.'}, status=404)

@api_view(['GET'])
def prbget_matches_scheduled(request):
    return JsonResponse({'message': 'prueba vista nueva'})
    
@api_view(['POST'])
def retrain_model(request):
    required_columns = ['AwayTeam', 'HF', 'AC', 'AR', 'FTAG', 'HST', 'HY', 'FTHG', 'HS', 'AF', 'AY', 'AS', 'AST', 'HomeTeam', 'HC']

    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No se ha proporcionado ningún archivo.'}, status=400)

        file = request.FILES['file']
        df = pd.read_csv(file)

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({'error': f'Faltan las siguientes columnas requeridas: {", ".join(missing_columns)}'}, status=400)

        result = retrain_model_logic(df)

        return JsonResponse({'message': 'Archivo leído correctamente. ' + result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
