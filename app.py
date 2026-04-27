import os
import math
from datetime import date, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Goal, DailyLog, MealLog, BodyProfile

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
    "meal": "elevator_02_refined.jpg",
    "water": "anime_05.webp",
    "workouts": "anime_03.webp",
    "power": "anime_11.webp",
    "saq": "anime_12.webp",
    "sleep": "anime_08.webp",
    "body": "anime_15.webp",
    "recovery": "anime_17.webp",
    "supplements": "anime_14.webp",
    "score": "elevator_04_refined.jpg",
    "background_grid": "anime_grid_background.jpg",
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


FOOD_DATABASE = {
    "rice": {"calories": 205, "protein_g": 4.3, "carbs_g": 44.5, "fat_g": 0.4, "sugar_g": 0.1, "sodium_mg": 2, "fiber_g": 0.6},
    "broccoli": {"calories": 55, "protein_g": 3.7, "carbs_g": 11.2, "fat_g": 0.6, "sugar_g": 2.2, "sodium_mg": 64, "fiber_g": 5.1},
    "grilled chicken": {"calories": 335, "protein_g": 62, "carbs_g": 0, "fat_g": 7.2, "sugar_g": 0, "sodium_mg": 180, "fiber_g": 0},
    "chicken": {"calories": 335, "protein_g": 62, "carbs_g": 0, "fat_g": 7.2, "sugar_g": 0, "sodium_mg": 180, "fiber_g": 0},
    "egg": {"calories": 78, "protein_g": 6.3, "carbs_g": 0.6, "fat_g": 5.3, "sugar_g": 0.4, "sodium_mg": 62, "fiber_g": 0},
    "eggs": {"calories": 78, "protein_g": 6.3, "carbs_g": 0.6, "fat_g": 5.3, "sugar_g": 0.4, "sodium_mg": 62, "fiber_g": 0},
    "banana": {"calories": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.4, "sugar_g": 14.4, "sodium_mg": 1, "fiber_g": 3.1},
    "apple": {"calories": 95, "protein_g": 0.5, "carbs_g": 25, "fat_g": 0.3, "sugar_g": 19, "sodium_mg": 2, "fiber_g": 4.4},
    "protein shake": {"calories": 160, "protein_g": 30, "carbs_g": 5, "fat_g": 2, "sugar_g": 2, "sodium_mg": 170, "fiber_g": 1},
    "soda": {"calories": 150, "protein_g": 0, "carbs_g": 39, "fat_g": 0, "sugar_g": 39, "sodium_mg": 45, "fiber_g": 0},
}

def estimate_meal(description):
    text = (description or "").lower().replace(",", " ")
    totals = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "sugar_g": 0, "sodium_mg": 0, "fiber_g": 0}
    for pattern, key in [
        (r"(\d+(?:\.\d+)?)\s*g(?:rams)?\s*(?:of\s*)?sugar", "sugar_g"),
        (r"(\d+(?:\.\d+)?)\s*g(?:rams)?\s*(?:of\s*)?protein", "protein_g"),
        (r"(\d+(?:\.\d+)?)\s*g(?:rams)?\s*(?:of\s*)?carbs?", "carbs_g"),
        (r"(\d+(?:\.\d+)?)\s*g(?:rams)?\s*(?:of\s*)?fat", "fat_g"),
        (r"(\d+(?:\.\d+)?)\s*mg\s*(?:of\s*)?sodium", "sodium_mg"),
        (r"(\d+(?:\.\d+)?)\s*g(?:rams)?\s*(?:of\s*)?fiber", "fiber_g"),
    ]:
        for match in re.finditer(pattern, text):
            amount = float(match.group(1)); totals[key] += amount
            if key == "sugar_g": totals["carbs_g"] += amount; totals["calories"] += amount * 4
            elif key in ["protein_g","carbs_g"]: totals["calories"] += amount * 4
            elif key == "fat_g": totals["calories"] += amount * 9
    for food, macros in FOOD_DATABASE.items():
        if food in text:
            qty = 1.0
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:cups?|cup|servings?|serving|scoops?|scoop|pieces?|piece)?\s+" + re.escape(food), text)
            if m: qty = float(m.group(1))
            for key in totals: totals[key] += macros[key] * qty
    score = 50
    score += 20 if totals["protein_g"] >= 30 else 10 if totals["protein_g"] >= 15 else 0
    score += 10 if totals["fiber_g"] >= 5 else 0
    score -= 30 if totals["sugar_g"] > 35 else 15 if totals["sugar_g"] > 20 else 0
    score -= 25 if totals["sodium_mg"] > 1200 else 12 if totals["sodium_mg"] > 750 else 0
    score -= 15 if totals["calories"] > 1100 else 0
    score += 10 if 350 <= totals["calories"] <= 850 else 0
    score = max(0, min(100, round(score)))
    return totals, score, "green" if score >= 75 else "yellow" if score >= 50 else "red"

def get_body_profile(user_id):
    profile = BodyProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = BodyProfile(user_id=user_id); db.session.add(profile); db.session.commit()
    return profile

def body_metrics(profile, current_weight):
    height = profile.height_in or 70; weight = current_weight or 0
    bmi = round((weight / (height * height)) * 703, 1) if weight and height else 0
    bmi_status = "green" if 18.5 <= bmi < 25 else "yellow" if 25 <= bmi < 30 else "red"
    bf = profile.body_fat_percent
    if not bf and profile.waist_in and profile.neck_in and height:
        try:
            if profile.sex == "female" and profile.hip_in:
                bf = 163.205 * math.log10(profile.waist_in + profile.hip_in - profile.neck_in) - 97.684 * math.log10(height) - 78.387
            else:
                bf = 86.010 * math.log10(profile.waist_in - profile.neck_in) - 70.041 * math.log10(height) + 36.76
            bf = round(max(3, min(65, bf)), 1)
        except Exception: bf = None
    bf_status = "yellow"
    if bf is not None:
        bf_status = "green" if ((profile.sex == "female" and 21 <= bf <= 31) or (profile.sex != "female" and 10 <= bf <= 20)) else "yellow" if bf <= 36 else "red"
    return {"bmi": bmi, "bmi_status": bmi_status, "body_fat": bf, "body_fat_status": bf_status}

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
    body_profile = get_body_profile(user_id)

    days = int(request.args.get("days", 7))
    if days not in [1, 7, 14, 30, 90, 180, 365, 9999]:
        days = 7
    start = date.today() - timedelta(days=days-1)
    logs = DailyLog.query.filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start
    ).order_by(DailyLog.log_date.asc()).all()

    by_date = {l.log_date: l for l in logs}
    labels, workout_data, calorie_data, sleep_data, sugar_data, sodium_data, protein_data = [], [], [], [], [], [], []
    for i in range(days):
        d = start + timedelta(days=i)
        l = by_date.get(d)
        labels.append(d.strftime("%a"))
        workout_data.append(l.workouts if l else 0)
        calorie_data.append(l.calories if l else 0)
        sleep_data.append(l.sleep_hours if l else 0)
        day_meals = MealLog.query.filter_by(user_id=user_id, log_date=d).all()
        sugar_data.append(round(sum(m.sugar_g for m in day_meals), 1))
        sodium_data.append(round(sum(m.sodium_mg for m in day_meals), 1))
        protein_data.append(round(sum(m.protein_g for m in day_meals), 1))


    today_meals = MealLog.query.filter_by(user_id=user_id, log_date=date.today()).order_by(MealLog.created_at.desc()).all()
    meal_totals = {
        "calories": round(sum(m.calories for m in today_meals), 1),
        "protein_g": round(sum(m.protein_g for m in today_meals), 1),
        "carbs_g": round(sum(m.carbs_g for m in today_meals), 1),
        "fat_g": round(sum(m.fat_g for m in today_meals), 1),
        "sugar_g": round(sum(m.sugar_g for m in today_meals), 1),
        "sodium_mg": round(sum(m.sodium_mg for m in today_meals), 1),
        "fiber_g": round(sum(m.fiber_g for m in today_meals), 1),
    }
    meal_day_score = 50
    if meal_totals["protein_g"] >= goals.protein_g * 0.8: meal_day_score += 20
    if meal_totals["sugar_g"] <= 36: meal_day_score += 15
    elif meal_totals["sugar_g"] > 60: meal_day_score -= 25
    if meal_totals["sodium_mg"] <= 2300: meal_day_score += 10
    elif meal_totals["sodium_mg"] > 3000: meal_day_score -= 25
    if meal_totals["fiber_g"] >= 25: meal_day_score += 10
    meal_day_score = max(0, min(100, round(meal_day_score)))
    meal_day_color = "green" if meal_day_score >= 75 else "yellow" if meal_day_score >= 50 else "red"
    body_summary = body_metrics(body_profile, log.body_weight or goals.body_weight_goal)

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
        "days": days,
        "workouts": workout_data,
        "calories": calorie_data,
        "sleep": sleep_data,
        "sugar": sugar_data,
        "sodium": sodium_data,
        "protein": protein_data,
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
        quotes=QUOTES,
        active_days=days,
        today_meals=today_meals,
        meal_totals=meal_totals,
        meal_day_score=meal_day_score,
        meal_day_color=meal_day_color,
        body_profile=body_profile,
        body_summary=body_summary,
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



@app.route("/meal", methods=["POST"])
@login_required
def add_meal():
    user_id = session["user_id"]; description = request.form.get("meal_description", "").strip()
    meal_type = request.form.get("meal_type", "meal").strip() or "meal"
    if not description: return redirect(url_for("dashboard"))
    totals, score, color = estimate_meal(description)
    for form_key, macro_key in {"manual_calories":"calories","manual_protein_g":"protein_g","manual_carbs_g":"carbs_g","manual_fat_g":"fat_g","manual_sugar_g":"sugar_g","manual_sodium_mg":"sodium_mg","manual_fiber_g":"fiber_g"}.items():
        val = request.form.get(form_key)
        if val not in (None, ""): totals[macro_key] = float(val)
    totals, score, color = totals, max(0, min(100, score)), color
    meal = MealLog(user_id=user_id, meal_type=meal_type, description=description, calories=round(totals["calories"],1), protein_g=round(totals["protein_g"],1), carbs_g=round(totals["carbs_g"],1), fat_g=round(totals["fat_g"],1), sugar_g=round(totals["sugar_g"],1), sodium_mg=round(totals["sodium_mg"],1), fiber_g=round(totals["fiber_g"],1), quality_color=color, quality_score=score)
    db.session.add(meal)
    daily = get_today_log(user_id); daily.calories += int(round(totals["calories"])); daily.protein_g += int(round(totals["protein_g"]))
    db.session.commit(); return redirect(url_for("dashboard"))

@app.route("/body-profile", methods=["POST"])
@login_required
def update_body_profile():
    profile = get_body_profile(session["user_id"])
    for field in ["height_in", "age", "waist_in", "neck_in", "hip_in", "body_fat_percent"]:
        val = request.form.get(field)
        if val not in (None, ""): setattr(profile, field, float(val) if field != "age" else int(float(val)))
    if request.form.get("sex"): profile.sex = request.form.get("sex")
    weight = request.form.get("body_weight")
    if weight not in (None, ""): get_today_log(session["user_id"]).body_weight = float(weight)
    db.session.commit(); return redirect(url_for("dashboard"))


@app.route("/api/weekly")
@login_required
def weekly_api():
    user_id = session["user_id"]
    days = int(request.args.get("days", 7))
    if days not in [1, 7, 14, 30, 90, 180, 365, 9999]:
        days = 7
    start = date.today() - timedelta(days=days-1)
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
