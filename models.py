from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(180), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    water_oz = db.Column(db.Integer, default=128)
    calories = db.Column(db.Integer, default=2300)
    protein_g = db.Column(db.Integer, default=190)
    workouts = db.Column(db.Integer, default=1)
    power_drills = db.Column(db.Integer, default=1)
    saq_minutes = db.Column(db.Integer, default=15)
    sleep_hours = db.Column(db.Float, default=7.0)
    recovery_minutes = db.Column(db.Integer, default=10)
    supplements = db.Column(db.Integer, default=1)
    body_weight_goal = db.Column(db.Float, default=185.0)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    log_date = db.Column(db.Date, default=date.today, index=True)

    water_oz = db.Column(db.Integer, default=0)
    calories = db.Column(db.Integer, default=0)
    protein_g = db.Column(db.Integer, default=0)
    workouts = db.Column(db.Integer, default=0)
    power_drills = db.Column(db.Integer, default=0)
    saq_minutes = db.Column(db.Integer, default=0)
    sleep_hours = db.Column(db.Float, default=0)
    recovery_minutes = db.Column(db.Integer, default=0)
    supplements = db.Column(db.Integer, default=0)
    body_weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, default="")

    __table_args__ = (db.UniqueConstraint("user_id", "log_date", name="one_log_per_user_per_day"),)
