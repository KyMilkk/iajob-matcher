import re
import string
import pandas as pd

def clean_text(text):
    text = text.lower() # Convierte el texto a minúsculas
    text = re.sub(r'\[.*?\]', ' ', text) # Elimina cualquier texto entre corchetes
    text = re.sub(r"\\W", " ", text) # Elimina cualquier carácter no alfanumérico
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text) # Elimina URLs
    text = re.sub(r'<.*?>+', ' ', text) # Elimina cualquier etiqueta HTML
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text) # Elimina signos de puntuación
    text = re.sub(r'\n', ' ', text) # Elimina saltos de línea
    text = re.sub(r'\w*\d\w*', ' ', text) # Elimina palabras que contienen números
   # text = re.sub('\s+', '', text)
    return text

def preprocess_data(resume_df, job_df):
    # Limpiar los textos de los CVs y las ofertas de empleo
    resume_df['Resume'] = resume_df['Resume'].apply(clean_text)
    job_df['job_title'] = job_df['job_title'].apply(clean_text)

    return resume_df, job_df

# Cargar los datasets
resume_df = pd.read_csv('data/raw/resume.csv', encoding='utf-8')
job_df = pd.read_csv('data/raw/job.csv', encoding='utf-8')

resume_df, job_df = preprocess_data(resume_df, job_df)

# Guardar los datos preprocesados
resume_df.to_csv('data/cleaned/resume_clean.csv', index=False, encoding='utf-8')
job_df.to_csv('data/cleaned/job_clean.csv', index=False, encoding='utf-8')
