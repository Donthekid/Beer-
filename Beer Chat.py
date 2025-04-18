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
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Press Start 2P', monospace;
            background-color: #2e2e2e;
            color: #ffcc66;
            text-align: center;
            padding: 40px;
        }
        h1 {
            font-size: 20px;
            color: #fff1c1;
        }
        .panel {
            background-color: rgba(0, 0, 0, 0.7);
            border: 4px solid #d4a24b;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto 30px;
            border-radius: 10px;
        }
        .beer-area {
            position: relative;
            height: 220px;
            margin-bottom: 20px;
        }
        .tap {
            width: 100px;
        }
        .glass {
            width: 80px;
            transition: transform 1s ease-out, opacity 1s ease-out;
        }
        .slide-out {
            transform: translateX(150%) translateY(-50px);
            opacity: 0;
        }
        .foam {
            display: block;
            height: 10px;
            background: #fffbe0;
            margin: 0 auto;
            width: 90px;
            border-radius: 10px;
        }
        .tab-buttons button {
            padding: 10px;
            font-size: 10px;
            margin: 5px;
            background: #444;
            color: #fff;
            border: 2px solid #d4a24b;
            cursor: pointer;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 8px;
            border-bottom: 1px solid #d4a24b;
        }
        form { display: inline; }
        .buttons button {
            background-color: #ffcc66;
            border: none;
            padding: 5px 10px;
            margin: 2px;
            cursor: pointer;
        }
    </style>
    <script>
        function showTab(id) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }
        function triggerGlassAnimation() {
            const glass = document.getElementById('beer-glass');
            glass.src = 'https://i.imgur.com/kMVMH4h.png';
            glass.classList.add('slide-out');
            setTimeout(() => {
                glass.classList.remove('slide-out');
                glass.src = 'https://i.imgur.com/qtjA0oQ.png';
            }, 2000);
        }
        window.onload = () => showTab('total');
    </script>
</head>
<body>
    <h1>🍺 1 MILLION BEERS 🍺</h1>
    <div class="panel">
        <img class="tap" src="https://i.imgur.com/NmUJbEX.png" alt="Tap">
        <div class="foam"></div>
        <img id="beer-glass" class="glass" src="https://i.imgur.com/qtjA0oQ.png" alt="Beer Glass">
        <div style="margin-top: 20px; font-size: 14px; color: #fff">Total Beers Consumed: {{ grand_total }}</div>
    </div>

    <div class="tab-buttons">
        <button onclick="showTab('total')">Total</button>
        <button onclick="showTab('weekly')">Weekly</button>
        <button onclick="showTab('monthly')">Monthly</button>
    </div>

    {% for label, stats, id in [('Total', total, 'total'), ('This Week', weekly, 'weekly'), ('This Month', monthly, 'monthly')] %}
    <div class="panel tab-content" id="{{ id }}">
        <h2>{{ label }} Leaderboard</h2>
        <table>
            <tr><th>#</th><th>Name</th><th>Beers</th><th>Add</th></tr>
            {% for row in stats %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ row[0] }}<br>
                    {% if loop.index <= 5 and row[1] > 0 %}<small><em>{{ titles[loop.index0] }}</em></small>{% endif %}
                    {% if row[1] == 0 %}<small><em>Virgin</em></small>{% endif %}
                </td>
                <td>{{ row[1] }}</td>
                <td class="buttons">
                    <form action="/add/{{ row[0] }}/1" method="post" onsubmit="triggerGlassAnimation()">
                        <button type="submit">+1</button>
                    </form>
                    <form action="/add/{{ row[0] }}/5" method="post" onsubmit="triggerGlassAnimation()">
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