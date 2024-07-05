import joblib
import tensorflow as tf
import numpy as np
import os
from django.conf import settings
import pandas as pd

# Ruta a los archivos de preprocesamiento y modelo
PREPROCESSOR_PATH = os.path.join(settings.BASE_DIR, 'analysis_app', 'models', 'preprocessing.pkl')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'analysis_app', 'models', 'best_model.h5')

# Cargar el preprocesador
with open(PREPROCESSOR_PATH, 'rb') as f:
    ordinal_encoder, scaler, best_pca, best_selected_features = joblib.load(f)

# Cargar el modelo sin argumentos no válidos
def custom_objects():
    custom_objects = {
        'LSTM': tf.keras.layers.LSTM
    }
    return custom_objects

model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects())

def preprocess_input(data):
    # Crear un DataFrame con las características necesarias
    new_match_data = {feature: 0 for feature in best_selected_features}
    new_match_data['HomeTeam'] = data['HomeTeam']
    new_match_data['AwayTeam'] = data['AwayTeam']
    new_match_df = pd.DataFrame([new_match_data])
    
    # Aplicar el preprocesador
    new_match_df[['HomeTeam', 'AwayTeam']] = ordinal_encoder.transform(new_match_df[['HomeTeam', 'AwayTeam']])
    new_match_df[best_selected_features] = scaler.transform(new_match_df[best_selected_features])
    new_match_pca = best_pca.transform(new_match_df[best_selected_features])
    
    return new_match_pca.reshape((1, new_match_pca.shape[1], 1))

def predict(data):
    # Preprocesar los datos de entrada
    try:
        processed_data = preprocess_input(data)
    except IndexError as e:
        return {'error': 'list index out of range. Please provide correct data format: {"HomeTeam": "TeamA", "AwayTeam": "TeamB"}.'}
    except Exception as e:
        return {'error': str(e)}

    # Hacer la predicción usando el modelo cargado
    prediction = model.predict(processed_data)
    predicted_class = np.argmax(prediction, axis=1)
    result_map = {0: 'Local gana', 1: 'Empate', 2: 'Visitante gana'}
    return result_map[predicted_class[0]]
