from database import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    preferred_start_date = db.Column(db.Date)
    expected_ctc = db.Column(db.String(50))
    experience = db.Column(db.String(50))
    skills = db.Column(db.Text)

    recommendations = db.relationship('Recommendation', backref='user', lazy=True)

class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    ctc_min = db.Column(db.Integer)
    ctc_max = db.Column(db.Integer)
    required_experience = db.Column(db.String(50))
    skills = db.Column(db.Text)
    job_title_encoded = db.Column(db.Integer, nullable=True)
    location_encoded = db.Column(db.Integer, nullable=True)
    ctc_min_scaled = db.Column(db.Float, nullable=True)
    ctc_max_scaled = db.Column(db.Float, nullable=True)

    recommendations = db.relationship('Recommendation', backref='job', lazy=True)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    rec_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    relevance_score = db.Column(db.Float)