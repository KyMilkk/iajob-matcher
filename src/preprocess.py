import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import re
import pickle

def preprocess_jobs(file_path):
    # Cargar el dataset de trabajos
    jobs_df = pd.read_csv(file_path)
    
    def extract_ctc_values(ctc_value):
        # Eliminar el símbolo de moneda y las comas
        ctc_clean = ctc_value.replace('₹', '').replace(',', '')
        # Encontrar todos los números
        numbers = re.findall(r'\d+', ctc_clean)
        if len(numbers) == 1:
            # Solo un monto presente
            return int(numbers[0]), int(numbers[0])
        elif len(numbers) == 2:
            # Rango presente
            return int(numbers[0]), int(numbers[1])
        else:
            # Valor predeterminado en caso de error
            return 0, 0
    
    # Aplicar la extracción de valores
    jobs_df[['ctc_min', 'ctc_max']] = jobs_df['ctc'].apply(lambda x: pd.Series(extract_ctc_values(x)))
    
    # Codificar las ubicaciones y títulos de trabajo
    le_location = LabelEncoder()
    le_title = LabelEncoder()
    jobs_df['location_encoded'] = le_location.fit_transform(jobs_df['location'])
    jobs_df['job_title_encoded'] = le_title.fit_transform(jobs_df['job_title'])
    
    # Escalar los valores de CTC
    scaler = MinMaxScaler()
    jobs_df[['ctc_min_scaled', 'ctc_max_scaled']] = scaler.fit_transform(jobs_df[['ctc_min', 'ctc_max']])

        # Guardar los datos procesados para depuración
    jobs_df.to_csv('data/processed/debug_processed_jobs.csv', index=False)

    print("Preprocesado del dataset job realizado")
    
    return jobs_df, le_location, le_title, scaler

def preprocess_users(file_path, le_location, scaler):
    # Cargar el dataset de usuarios
    users_df = pd.read_csv(file_path)
    
    # Codificar las ubicaciones
    users_df['location_encoded'] = le_location.transform(users_df['location'])
    
    # Extraer y escalar el CTC esperado
    def extract_user_ctc_values(ctc_value):
        # Eliminar el símbolo de moneda y las comas
        ctc_clean = ctc_value.replace('₹', '').replace(',', '')
        # Encontrar todos los números
        numbers = re.findall(r'\d+', ctc_clean)
        if len(numbers) == 1:
            # Solo un monto presente
            return int(numbers[0]), int(numbers[0])
        elif len(numbers) == 2:
            # Rango presente
            return int(numbers[0]), int(numbers[1])
        else:
            # Valor predeterminado en caso de error
            return 0, 0

    # Aplicar la extracción de valores
    users_df[['ctc_min', 'ctc_max']] = users_df['expected_ctc'].apply(lambda x: pd.Series(extract_user_ctc_values(x)))
    users_df[['ctc_min_scaled', 'ctc_max_scaled']] = scaler.transform(users_df[['ctc_min', 'ctc_max']])
    
    users_df.to_csv('data/processed/debug_processed_users.csv', index=False)

    print("Preprocesado del dataset user_data realizado")

    return users_df

if __name__ == "__main__":
    jobs_df, le_location, le_title, scaler = preprocess_jobs('data/raw/job.csv')
    users_df = preprocess_users('data/raw/user_data.csv', le_location, scaler)
    
    # Guardar los datasets procesados
    jobs_df.to_csv('data/processed/processed_jobs.csv', index=False)
    users_df.to_csv('data/processed/processed_users.csv', index=False)


# Guardar LabelEncoders y Scaler
with open('src/le_location.pkl', 'wb') as f:
    pickle.dump(le_location, f)

with open('src/le_title.pkl', 'wb') as f:
    pickle.dump(le_title, f)

with open('src/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)