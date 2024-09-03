from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
import os
import sys
import io
from database import db
from decouple import config

app = Flask(__name__)
app.secret_key = config('SECRET_KEY')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/iajob_matcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Importar modelos después de inicializar SQLAlchemy
from models import User, Job, Recommendation

# Cargar el modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'job_recommendation_model.keras')
model = load_model(MODEL_PATH)

# Cargar los LabelEncoders y Scaler previamente entrenados
LE_LOCATION_PATH = os.path.join(os.path.dirname(__file__), 'le_location.pkl')
LE_TITLE_PATH = os.path.join(os.path.dirname(__file__), 'le_title.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

with open(LE_LOCATION_PATH, 'rb') as f:
    le_location = pickle.load(f)

with open(LE_TITLE_PATH, 'rb') as f:
    le_title = pickle.load(f)

with open(SCALER_PATH, 'rb') as f:
    scaler = pickle.load(f)


@app.route('/')
def home():
    user_name = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user_name = user.user_name
    return render_template('index.html', user_name=user_name)

# Registro de Usuarios
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        # Obtener datos del formulario
        user_name = request.form['user_name']
        location = request.form['location']
        preferred_start_date = request.form['preferred_start_date']
        expected_ctc = request.form['expected_ctc']
        experience = request.form['experience']
        skills = request.form['skills']

        # Crear un nuevo usuario
        new_user = User(
            user_name=user_name,
            location=location,
            preferred_start_date=preferred_start_date,
            expected_ctc=expected_ctc,
            experience=experience,
            skills=skills
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.user_id
            flash('Usuario registrado exitosamente!', 'success')
            print(f"Redirigiendo a recomendaciones para el usuario con ID: {new_user.user_id}")
            return redirect(url_for('get_recommendations', user_id=new_user.user_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el usuario: {e}', 'danger')
            return redirect(url_for('register_user'))

    return render_template('miperfil.html')

# Recomendaciones
@app.route('/recommendations/<int:user_id>')
def get_recommendations(user_id):
    # Obtener el usuario
    user = User.query.get_or_404(user_id)
    # Preprocesar los datos del usuario
    user_data = preprocess_user(user)

    # Obtener todos los trabajos
    jobs = Job.query.all()
    job_data = preprocess_jobs(jobs)

    # Generar pares para predicción
    X = generate_features(job_data, user_data)

    # Imprime los primeros 5 elementos de X para depuración
    print("Datos de entrada X para predicción:")
    print(X[:5])

    # Guardar datos de depuración
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
      try:
        f.write(f"User Data: {user_data}\n")
        f.write(f"Job Data: {job_data}\n")
        f.write(f"Features (X): {X}\n")
      except UnicodeEncodeError as e:
        f.write(f"Error encoding data: {e}\n")

    # Hacer predicciones
    predictions = model.predict(X).flatten()

    # Asociar las predicciones con los trabajos
    recommendations = []
    for job, score in zip(jobs, predictions):
        recommendations.append({'job': job, 'score': score})

    # Ordenar las recomendaciones por puntuación descendente
    recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:10]  # Top 10

    # Guardar recomendaciones en la base de datos
    for rec in recommendations:
        recommendation = Recommendation(
            user_id=user_id,
            job_id=rec['job'].job_id,
            relevance_score=float(rec['score'])
        )
        db.session.add(recommendation)
    
    db.session.commit()

    return render_template('recommendations.html', user=user, recommendations=recommendations)

# Buscador
@app.route('/search')
def search():

    # - - - -

    return render_template('buscador.html')

# Preprocesamiento



def extract_ctc(expected_ctc):
    # Extraer ctc_min y ctc_max de la cadena
    import re
    numbers = re.findall(r'\d+', expected_ctc.replace('₹', '').replace(',', ''))
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    elif len(numbers) == 1:
        return int(numbers[0]), int(numbers[0])
    else:
        return 0, 0

def preprocess_user(user):
    # Codificar la ubicación del usuario
    try:
        user_location_encoded = le_location.transform([user.location])[0]
    except:
        user_location_encoded = le_location.transform(['Unknown'])[0]  # Manejar ubicaciones desconocidas

    # Extraer y escalar el CTC esperado
    ctc_min, ctc_max = extract_ctc(user.expected_ctc)
    ctc_scaled = scaler.transform([[ctc_min, ctc_max]])[0]

    # Aquí puedes agregar más preprocesamiento según sea necesario
    return {
        'user_location_encoded': user_location_encoded,
        'user_ctc_min_scaled': ctc_scaled[0],
        'user_ctc_max_scaled': ctc_scaled[1]
    }

def preprocess_jobs(jobs):
    job_features = []
    for job in jobs:
        # Codificar la ubicación del trabajo
        try:
            job_location_encoded = le_location.transform([job.location])[0]
        except:
            job_location_encoded = le_location.transform(['Unknown'])[0]

        # Extraer y escalar el CTC
        ctc_scaled = scaler.transform([[job.ctc_min, job.ctc_max]])[0]

        job_features.append({
            'job_title_encoded': job.job_title_encoded,
            'location_encoded': job_location_encoded,
            'ctc_min_scaled': ctc_scaled[0],
            'ctc_max_scaled': ctc_scaled[1]
        })
    return job_features

def generate_features(job_data, user_data):
    features = []
    for job in job_data:
        feature = [
            job['job_title_encoded'],
            job['location_encoded'],
            job['ctc_min_scaled'],
            job['ctc_max_scaled'],
            user_data['user_location_encoded'],
            user_data['user_ctc_min_scaled'],
            user_data['user_ctc_max_scaled']
        ]
        features.append(feature)
    return np.array(features)

if __name__ == '__main__':
    app.run(debug=True)

from flask_migrate import Migrate

migrate = Migrate(app, db)