from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import os
from database import db
from decouple import config

app = Flask(__name__)
app.secret_key = config('SECRET_KEY')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/iajob_matcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Importar modelos después de inicializar SQLAlchemy
from models import User, Job, Recommendation

# Cargar el modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'job_recommendation_model.keras')
model = load_model(MODEL_PATH)

@app.route('/')
def home():
    return render_template('index.html')

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
            flash('Usuario registrado exitosamente!', 'success')
            return redirect(url_for('home'))
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


def preprocess_user(user):
    # Implementa el preprocesamiento similar al script de preprocesamiento
    # Por ejemplo, codificar la ubicación, escalar el CTC esperado, etc.
    # Aquí se asume que ya tienes los LabelEncoders y Scalers cargados
    # Para simplificar, este ejemplo no los incluye
    # Debes adaptar esto según tu implementación
    # Por ejemplo:
    # user_location_encoded = le_location.transform([user.location])[0]
    # ctc_min, ctc_max = extract_ctc(user.expected_ctc)
    # ctc_scaled = scaler.transform([[ctc_min, ctc_max]])[0]
    pass

def preprocess_jobs(jobs):
    # Implementa el preprocesamiento similar al script de preprocesamiento
    # Debes adaptar esto según tu implementación
    pass

def generate_features(job_data, user_data):
    # Combina las características de trabajos y usuarios para crear las entradas al modelo
    # Debes adaptar esto según tu implementación
    pass

if __name__ == '__main__':
    app.run(debug=True)

from flask_migrate import Migrate

migrate = Migrate(app, db)