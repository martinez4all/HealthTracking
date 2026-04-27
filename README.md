# Warrior Health App

Anime-themed multi-user health dashboard built with Flask.

## Features
- User registration/login
- Separate private account data for each user
- Adjustable goals per account
- Daily logs for water, food, workouts, power drills, SAQ, sleep, recovery, supplements, body metrics
- Dashboard styled to match the approved anime mockup
- Chart.js weekly progress graph
- Ready for GitHub + Render deployment

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python app.py
```

Open:
http://127.0.0.1:5000

## Render
Push to GitHub, connect the repo in Render, and use:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

For production, add a PostgreSQL database in Render and set DATABASE_URL automatically.


## Fix Update
This version fixes:
- Weekly Progress horizontal scroll issue
- Sidebar links now go to real connected pages
- Goals, Notes, and Supplements pages have working forms


## V4 HARD FIX
- Recent Activity is forced to the bottom of the page.
- Bottom dashboard panels use vertical flex layout, not side-by-side grid.
- No horizontal overflow or hidden right panel.


## V6 Polish
- Left tabs are color-coded and stronger.
- Top quote rotates every 30 seconds.
- Time filter links now reload dashboard with selected range.
- Daily Score uses clearer Luffy image.
- New uploaded images form a subtle grid background.


## V7 Final Header / Background
- Removed top-left logo circle and brand quote.
- Header now says: "The cold water does not get warmer if you jump late."
- Header is huge, centered, white with subtle red glow.
- Uploaded image grid background is made more visible.
