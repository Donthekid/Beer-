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

TITLES = [
    "Alcoholic in Chief",
    "Deputy Degenerate",
    "Brewsketeer",
    "Pilsner Prodigy",
    "Certified Sipper"
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
        counts[name] += 1
    return counts

def build_ranking(counts):
    return sorted(((name, counts.get(name, 0)) for name in FRIENDS), key=lambda x: (-x[1], x[0]))

@app.route('/')
def leaderboard():
    data = load_data()
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
        data = load_data()
        for _ in range(amount):
            data.append({"name": name, "timestamp": datetime.now().isoformat()})
        save_data(data)
    return redirect(url_for('leaderboard'))

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>1 MILLION BEERS</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #fffaf2;
            text-align: center;
            padding: 20px;
            color: #333;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
        }
        .total-counter {
            font-size: 2em;
            margin: 10px 0 30px;
        }
        .tabs button {
            padding: 10px 20px;
            margin: 0 5px;
            cursor: pointer;
            font-weight: bold;
            border: 1px solid #ccc;
            background: #f5f5f5;
        }
        .tabs button.active {
            background: #ffe082;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        table {
            margin: auto;
            border-collapse: collapse;
            width: 100%;
            max-width: 700px;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .buttons form {
            display: inline;
            margin-left: 10px;
        }
    </style>
    <script>
        function showTab(id) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            document.querySelectorAll('.tabs button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + id).classList.add('active');
        }
        window.onload = () => showTab('total');
    </script>
</head>
<body>
    <h1>1 MILLION BEERS</h1>
    <div class="total-counter">Total Beers Consumed: 🍺 {{ grand_total }}</div>

    <div class="tabs">
        <button id="btn-total" onclick="showTab('total')">Total</button>
        <button id="btn-weekly" onclick="showTab('weekly')">This Week</button>
        <button id="btn-monthly" onclick="showTab('monthly')">This Month</button>
    </div>

    {% for label, stats, id in [('Total', total, 'total'), ('This Week', weekly, 'weekly'), ('This Month', monthly, 'monthly')] %}
    <div class="tab-content" id="{{ id }}">
        <h2>{{ label }} Leaderboard</h2>
        <table>
            <tr><th>Rank</th><th>Name</th><th>Beers</th><th>Add</th></tr>
            {% for row in stats %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>
                    {{ row[0] }}
                    {% if loop.index <= 5 and row[1] > 0 %}<br><small><em>{{ titles[loop.index0] }}</em></small>{% endif %}
                    {% if row[1] == 0 %}<br><small><em>Virgin</em></small>{% endif %}
                </td>
                <td>{{ row[1] }}</td>
                <td class="buttons">
                    <form action="/add/{{ row[0] }}/1" method="post">
                        <button type="submit">+1</button>
                    </form>
                    <form action="/add/{{ row[0] }}/5" method="post">
                        <button type="submit">+5</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</body>
</html>
'''

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)