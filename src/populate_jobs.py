from app import app
from database import db
from models import Job
import pandas as pd

def populate_jobs(csv_path):
    jobs_df = pd.read_csv(csv_path)

    with app.app_context():
        for _, row in jobs_df.iterrows():
            job = Job(
                job_title=row['job_title'],
                location=row['location'],
                ctc_min=row['ctc_min'],
                ctc_max=row['ctc_max'],
                required_experience=row['experience'],
                skills=row['company_name'],
                job_title_encoded=row['job_title_encoded'],
                location_encoded=row['location_encoded'],
                ctc_min_scaled=row['ctc_min_scaled'],
                ctc_max_scaled=row['ctc_max_scaled']
            )
            db.session.add(job)
        
        db.session.commit()
        print("Trabajos añadidos exitosamente.")

if __name__ == '__main__':
    with app.app_context():
        populate_jobs('data/processed/processed_jobs.csv')
