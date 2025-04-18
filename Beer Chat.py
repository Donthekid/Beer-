from flask import Flask, render_template_string, request, redirect, url_for
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)

DATA_FILE = 'beers.json'
FRIENDS = [
    "Daniel", "Eamon", "Carlos", "Gor", "Grace", "Jacob", "Josh", "Lauren",
    "Natalia", "Patrick", "Stephanie", "Sophia", "Alex", "Alora", "Amanda",
    "Anthony", "Bella", "Bradley", "Caitlin", "Carla", "Charlie", "Devin",
    "Devon", "Eleana", "Eunsung", "Fantasia", "Gracie", "Ina", "Jacquline",
    "Jasmine", "Jon", "Jonathon", "Kai", "Kenzie", "Khoudia", "Kira", "Lucas",
    "Narissa", "Nataly", "Nicolas", "Steven", "Sue", "Tessa", "Valentin"
]

# Load existing data or create empty list
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Count beers by time range
def count_beers(data, time_filter=None):
    counts = defaultdict(int)
    now = datetime.now()
    for entry in data:
        name = entry['name']
        time = datetime.fromisoformat(entry['timestamp'])
        if time_filter == 'week' and now - time > timedelta(days=7):
            continue
        elif time_filter == 'month' and now - time > timedelta(days=30):
            continue
        elif time_filter == 'semester' and now - time > timedelta(days=120):
            continue
        counts[name] += 1
    return counts

@app.route('/')
def leaderboard():
    data = load_data()
    total = count_beers(data)
    weekly = count_beers(data, 'week')
    monthly = count_beers(data, 'month')
    semester = count_beers(data, 'semester')

    def build_ranking(counts):
        return sorted(((name, counts.get(name, 0)) for name in FRIENDS), key=lambda x: x[1], reverse=True)

    return render_template_string(TEMPLATE,
        total=build_ranking(total),
        weekly=build_ranking(weekly),
        monthly=build_ranking(monthly),
        semester=build_ranking(semester),
        friends=FRIENDS
    )

@app.route('/add/<name>', methods=['POST'])
def add_beer(name):
    if name in FRIENDS:
        data = load_data()
        data.append({"name": name, "timestamp": datetime.now().isoformat()})
        save_data(data)
    return redirect(url_for('leaderboard'))

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>🍺 Beer Leaderboard</title>
    <style>
        body { font-family: sans-serif; text-align: center; }
        h2 { margin-top: 40px; }
        table { margin: auto; border-collapse: collapse; }
        td, th { padding: 8px 12px; border: 1px solid #ddd; }
        form { display: inline; }
        .name { width: 150px; text-align: left; }
    </style>
</head>
<body>
    <h1>🍺 Beer Leaderboard</h1>
    {% for label, stats in [('Total', total), ('This Week', weekly), ('This Month', monthly), ('This Semester', semester)] %}
    <h2>{{ label }}</h2>
    <table>
        <tr><th>Name</th><th>Beers</th></tr>
        {% for name, count in stats %}
        <tr><td class="name">{{ name }}</td><td>{{ count }}</td></tr>
        {% endfor %}
    </table>
    {% endfor %}

    <h2>Add a Beer 🍻</h2>
    <table>
        {% for name in friends %}
        <tr>
            <td class="name">{{ name }}</td>
            <td>
                <form action="/add/{{ name }}" method="post">
                    <button type="submit">+1 Beer</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

import os
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)

