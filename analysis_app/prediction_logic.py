from .predictor import predict
from .utils import fetch_teams_data
from django.core.cache import cache

def make_prediction_logic():
    cache_key = 'fetch_teams_data_PL'
    teams_data = cache.get(cache_key)
    
    if not teams_data:
        teams_data = fetch_teams_data()
        if not teams_data:
            raise Exception('No se encontraron datos de equipos.')
        cache.set(cache_key, teams_data, timeout=60*60*24)  # Cache por 24 horas

    home_team = teams_data['homeTeam']
    away_team = teams_data['awayTeam']
    
    # Prepara los datos de entrada para la predicción
    input_data = {'HomeTeam': home_team, 'AwayTeam': away_team}
    
    # Hacer la predicción
    prediction = predict(input_data)
    return prediction

def make_prediction_logic_without_teamdata(home_team_name, away_team_name):
    input_data = {'HomeTeam': home_team_name, 'AwayTeam': away_team_name}
    prediction = predict(input_data)
    return prediction
