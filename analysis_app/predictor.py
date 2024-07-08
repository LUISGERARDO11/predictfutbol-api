import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import os
from django.conf import settings

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

# Función para ajustar los nombres de los equipos
def adjust_team_names(team_name):
    adjustments = {
        'Leicester City': 'Leicester',
        'Wolverhampton': 'Wolves',
        'Brighton Hove': 'Brighton',
        'Nottingham': 'Nott\'m Forest'
    }
    return adjustments.get(team_name, team_name)

def preprocess_input(data):
    try:
        # Ajustar los nombres de los equipos
        data['HomeTeam'] = adjust_team_names(data['HomeTeam'])
        data['AwayTeam'] = adjust_team_names(data['AwayTeam'])

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
    except ValueError as e:
        unknown_categories = str(e).split("['")[1].split("']")[0]
        raise ValueError(f"Equipo(s) desconocido(s): {unknown_categories}. Por favor, usa equipos conocidos.")
    except Exception as e:
        raise e

def predict(data):
    try:
        # Preprocesar los datos de entrada
        processed_data = preprocess_input(data)
    except ValueError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}

    # Hacer la predicción usando el modelo cargado
    prediction = model.predict(processed_data)
    predicted_class = np.argmax(prediction, axis=1)
    result_map = {0: 'Local gana', 1: 'Empate', 2: 'Visitante gana'}
    return result_map[predicted_class[0]]

def retrain_model_logic(df):
    selected_features = ['AwayTeam', 'HF', 'AC', 'AR', 'FTAG', 'HST', 'HY', 'FTHG', 'HS', 'AF', 'AY', 'AS', 'AST', 'HomeTeam', 'HC']

    # Preprocesamiento
    df = df[selected_features + ['FTR']]
    df['FTR'] = df['FTR'].map({'H': 0, 'D': 1, 'A': 2})

    # Encode categorical variables
    ordinal_encoder = OrdinalEncoder()
    df[['HomeTeam', 'AwayTeam']] = ordinal_encoder.fit_transform(df[['HomeTeam', 'AwayTeam']])

    # Scale features
    scaler = StandardScaler()
    df[selected_features] = scaler.fit_transform(df[selected_features])

    # Apply PCA
    pca = PCA(n_components=14)
    df_pca = pca.fit_transform(df[selected_features])

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(df_pca, df['FTR'], test_size=0.2, random_state=42)

    # Convertir las etiquetas a formato categórico
    y_train = tf.keras.utils.to_categorical(y_train)
    y_test = tf.keras.utils.to_categorical(y_test)

    # Redimensionar los datos para LSTM
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Build the model
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.LSTM(units=128, input_shape=(X_train.shape[1], 1), return_sequences=True))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.LSTM(units=64, return_sequences=False))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(32, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(units=3, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=500, batch_size=64, validation_split=0.2, callbacks=[early_stopping])

    # Save the model and preprocessors
    model.save(MODEL_PATH)
    with open(PREPROCESSOR_PATH, 'wb') as f:
        joblib.dump((ordinal_encoder, scaler, pca, selected_features), f)

    return 'Modelo reentrenado y guardado exitosamente.'