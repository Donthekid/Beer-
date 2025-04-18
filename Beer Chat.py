from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)

DB_FILE = '/tmp/beers.db'
FRIENDS = [
    "Daniel", "Eamon", "Carlos", "Gor", "Grace", "Jacob", "Josh", "Lauren",
    "Natalia", "Patrick", "Stephanie", "Sophia", "Alex", "Alora", "Amanda",
    "Anthony", "Bella", "Bradley", "Caitlin", "Carla", "Charlie", "Devin",
    "Devon", "Eleana", "Eunsung", "Fantasia", "Gracie", "Ina", "Jacquline",
    "Jasmine", "Jon", "Jonathon", "Kai", "Kenzie", "Khoudia", "Kira", "Lucas",
    "Narissa", "Nataly", "Nicolas", "Steven", "Sue", "Tessa", "Valentin"
]

TITLES = [
    "Alcoholic in Chief",
    "Deputy Degenerate",
    "Brewsketeer",
    "Pilsner Prodigy",
    "Certified Sipper"
]

# Initialize SQLite DB

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS beers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)

def insert_beer(name):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO beers (name, timestamp) VALUES (?, ?)", (name, datetime.now().isoformat()))

def fetch_beers():
    with sqlite3.connect(DB_FILE) as conn:
        return conn.execute("SELECT name, timestamp FROM beers").fetchall()

def count_beers(data, time_filter=None):
    counts = defaultdict(int)
    now = datetime.now()
    for name, ts in data:
        time = datetime.fromisoformat(ts)
        if time_filter == 'week' and now - time > timedelta(days=7):
            continue
        elif time_filter == 'month' and now - time > timedelta(days=30):
            continue
        counts[name] += 1
    return counts

def build_ranking(counts):
    return sorted(((name, counts.get(name, 0)) for name in FRIENDS), key=lambda x: (-x[1], x[0]))

@app.route('/')
def leaderboard():
    data = fetch_beers()
    total = count_beers(data)
    weekly = count_beers(data, 'week')
    monthly = count_beers(data, 'month')
    grand_total = sum(total.values())

    return render_template_string(TEMPLATE,
        total=build_ranking(total),
        weekly=build_ranking(weekly),
        monthly=build_ranking(monthly),
        grand_total=grand_total,
        friends=FRIENDS,
        titles=TITLES
    )

@app.route('/add/<name>/<int:amount>', methods=['POST'])
def add_beer(name, amount):
    if name in FRIENDS:
        for _ in range(amount):
            insert_beer(name)
    return redirect(url_for('leaderboard'))

# The HTML TEMPLATE remains the same as in your current version
from flask import Markup
TEMPLATE = Markup('''
<!-- [KEEP YOUR EXISTING HTML TEMPLATE HERE] -->
''')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)