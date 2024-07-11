from .predictor import predict
from django.core.cache import cache

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

def make_prediction_logic_without_teamdata(home_team_name, away_team_name):
    input_data = {'HomeTeam': home_team_name, 'AwayTeam': away_team_name}
    prediction = predict(input_data)
    return prediction
