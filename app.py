import os
from datetime import date, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Goal, DailyLog

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-this-secret")

database_url = os.environ.get("DATABASE_URL", "sqlite:///warrior_health.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

CATEGORY_IMAGES = {
    "hero": "anime_01.webp",
    "food": "anime_02.webp",
    "water": "anime_05.webp",
    "workouts": "anime_03.webp",
    "power": "anime_11.webp",
    "saq": "anime_12.webp",
    "sleep": "anime_08.webp",
    "body": "anime_15.webp",
    "recovery": "anime_17.webp",
    "supplements": "anime_14.webp",
    "score": "anime_09.webp",
}

QUOTES = [
    "Flectere si nequeo superos, Acheronta movebo.",
    "Oderint dum metuant.",
    "Nec sorte, nec fato.",
    "Aut viam inveniam aut faciam.",
    "Quo non ascendam?",
    "Utere, non numera.",
    "Vincit qui se vincit.",
    "Non ducor, duco.",
    "Veritas lux mea.",
    "Si vis pacem, para bellum.",
    "The cold water does not get warmer if you jump late.",
    "Your ability to grow is directly tied to how much truth you can handle about yourself without trying to escape it.",
    "The only person coming to save you is the version of yourself that’s tired of your current situation.",
    "If you’re worried about the cost of going for it, you should see the price of staying exactly where you are.",
    "When you reach the peak, you realize the mountain wasn’t the obstacle, you were.",
    "A tree with no leaves won’t protect you from the rain, but the rain will protect you from a tree with no leaves.",
]

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return fn(*args, **kwargs)
    return wrapper

def get_today_log(user_id):
    today = date.today()
    log = DailyLog.query.filter_by(user_id=user_id, log_date=today).first()
    if not log:
        log = DailyLog(user_id=user_id, log_date=today)
        db.session.add(log)
        db.session.commit()
    return log

def get_user_goals(user_id):
    goals = Goal.query.filter_by(user_id=user_id).first()
    if not goals:
        goals = Goal(user_id=user_id)
        db.session.add(goals)
        db.session.commit()
    return goals

def percent(value, goal):
    if not goal or goal <= 0:
        return 0
    return min(round((value / goal) * 100), 100)

@app.before_request
def setup_database():
    if not getattr(app, "_db_ready", False):
        db.create_all()
        app._db_ready = True

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="login")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("auth.html", mode="login")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("auth.html", mode="register")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip() or None
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password are required.")
        return redirect(url_for("register_page"))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("That username already exists.")
        return redirect(url_for("register_page"))

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    db.session.add(Goal(user_id=user.id))
    db.session.commit()

    session["user_id"] = user.id
    session["username"] = user.username
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session["user_id"] = user.id
        session["username"] = user.username
        return redirect(url_for("dashboard"))

    flash("Login failed.")
    return redirect(url_for("login_page"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = User.query.get(user_id)
    goals = get_user_goals(user_id)
    log = get_today_log(user_id)

    start = date.today() - timedelta(days=6)
    logs = DailyLog.query.filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start
    ).order_by(DailyLog.log_date.asc()).all()

    by_date = {l.log_date: l for l in logs}
    labels, workout_data, calorie_data, sleep_data = [], [], [], []
    for i in range(7):
        d = start + timedelta(days=i)
        l = by_date.get(d)
        labels.append(d.strftime("%a"))
        workout_data.append(l.workouts if l else 0)
        calorie_data.append(l.calories if l else 0)
        sleep_data.append(l.sleep_hours if l else 0)

    score_parts = [
        percent(log.water_oz, goals.water_oz),
        percent(log.calories, goals.calories),
        percent(log.protein_g, goals.protein_g),
        percent(log.workouts, goals.workouts),
        percent(log.power_drills, goals.power_drills),
        percent(log.saq_minutes, goals.saq_minutes),
        percent(log.sleep_hours, goals.sleep_hours),
        percent(log.recovery_minutes, goals.recovery_minutes),
        percent(log.supplements, goals.supplements),
    ]
    health_score = round(sum(score_parts) / len(score_parts))

    progress = {
        "Food Intake": percent(log.calories, goals.calories),
        "Water Intake": percent(log.water_oz, goals.water_oz),
        "Workouts": percent(log.workouts, goals.workouts),
        "Power Drills": percent(log.power_drills, goals.power_drills),
        "SAQ Training": percent(log.saq_minutes, goals.saq_minutes),
        "Sleep": percent(log.sleep_hours, goals.sleep_hours),
        "Recovery": percent(log.recovery_minutes, goals.recovery_minutes),
        "Supplements": percent(log.supplements, goals.supplements),
    }

    chart_payload = {
        "labels": labels,
        "workouts": workout_data,
        "calories": calorie_data,
        "sleep": sleep_data,
    }

    return render_template(
        "dashboard.html",
        user=user,
        goals=goals,
        log=log,
        progress=progress,
        health_score=health_score,
        chart_payload=chart_payload,
        images=CATEGORY_IMAGES,
        quote=QUOTES[date.today().toordinal() % len(QUOTES)],
    )

@app.route("/log", methods=["POST"])
@login_required
def log_data():
    user_id = session["user_id"]
    log = get_today_log(user_id)

    number_fields = ["water_oz", "calories", "protein_g", "workouts", "power_drills", "saq_minutes", "recovery_minutes", "supplements"]
    for field in number_fields:
        val = request.form.get(field)
        if val not in (None, ""):
            setattr(log, field, getattr(log, field) + int(float(val)))

    sleep_val = request.form.get("sleep_hours")
    if sleep_val not in (None, ""):
        log.sleep_hours = float(sleep_val)

    body_weight = request.form.get("body_weight")
    if body_weight not in (None, ""):
        log.body_weight = float(body_weight)

    notes = request.form.get("notes")
    if notes:
        log.notes = (log.notes + "\n" + notes).strip()

    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/goals", methods=["POST"])
@login_required
def update_goals():
    goals = get_user_goals(session["user_id"])
    fields = ["water_oz", "calories", "protein_g", "workouts", "power_drills", "saq_minutes", "sleep_hours", "recovery_minutes", "supplements", "body_weight_goal"]
    for field in fields:
        val = request.form.get(field)
        if val not in (None, ""):
            setattr(goals, field, float(val) if field in ["sleep_hours", "body_weight_goal"] else int(float(val)))
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/page/<page_name>")
@login_required
def simple_page(page_name):
    allowed = {
        "calendar": "Calendar",
        "analytics": "Analytics",
        "progress": "Progress",
        "goals": "Goals",
        "challenges": "Challenges",
        "notes": "Notes",
        "supplements": "Supplements",
        "settings": "Settings",
    }
    title = allowed.get(page_name)
    if not title:
        return redirect(url_for("dashboard"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    goals = get_user_goals(user_id)
    log = get_today_log(user_id)

    return render_template(
        "page.html",
        user=user,
        title=title,
        page_name=page_name,
        goals=goals,
        log=log,
        images=CATEGORY_IMAGES,
    )


@app.route("/api/weekly")
@login_required
def weekly_api():
    user_id = session["user_id"]
    start = date.today() - timedelta(days=6)
    logs = DailyLog.query.filter(DailyLog.user_id == user_id, DailyLog.log_date >= start).order_by(DailyLog.log_date.asc()).all()
    return jsonify([
        {
            "date": l.log_date.isoformat(),
            "water_oz": l.water_oz,
            "calories": l.calories,
            "protein_g": l.protein_g,
            "workouts": l.workouts,
            "power_drills": l.power_drills,
            "saq_minutes": l.saq_minutes,
            "sleep_hours": l.sleep_hours,
            "recovery_minutes": l.recovery_minutes,
            "supplements": l.supplements,
            "body_weight": l.body_weight,
        }
        for l in logs
    ])

if __name__ == "__main__":
    app.run(debug=True)
