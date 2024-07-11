from .predictor import predict
from .utils import TEAMS_DATA

def make_prediction_logic():
    if not TEAMS_DATA:
        raise Exception('No se encontraron datos de equipos.')
    
    home_team = TEAMS_DATA['homeTeam']
    away_team = TEAMS_DATA['awayTeam']
    
    input_data = {'HomeTeam': home_team, 'AwayTeam': away_team}
    prediction = predict(input_data)
    return prediction

def make_prediction_logic_without_teamdata(home_team_name, away_team_name):
    input_data = {'HomeTeam': home_team_name, 'AwayTeam': away_team_name}
    prediction = predict(input_data)
    return prediction
