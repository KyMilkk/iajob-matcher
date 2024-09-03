import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Embedding, Flatten
from sklearn.model_selection import train_test_split
import sys
import io

# Configurar la codificación estándar
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_data():
    jobs_df = pd.read_csv('data/processed/processed_jobs.csv')
    users_df = pd.read_csv('data/processed/processed_users.csv')
    
    # Creación del dataset de entrenamiento
    X = np.hstack([
        jobs_df[['job_title_encoded', 'location_encoded', 'ctc_min_scaled', 'ctc_max_scaled']].values,
        users_df[['location_encoded', 'ctc_min_scaled', 'ctc_max_scaled']].values
    ])
    
    # Generar etiquetas de relevancia (1 relevante, 0 no relevante)
    y = np.random.randint(0, 2, X.shape[0])  # Generar etiquetas aleatorias (para ejemplo)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def build_model(input_dim):
    model = Sequential()
    model.add(Dense(128, input_dim=input_dim, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    
    model = build_model(X_train.shape[1])
    
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))  # Aumentar épocas
    
    # Guardar el modelo entrenado en formato Keras
    model.save('src/job_recommendation_model.keras')
