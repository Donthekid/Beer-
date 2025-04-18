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
            background-image: url('https://i.imgur.com/vOeGzTp.png');
            background-size: cover;
            color: #ffcc66;
            text-align: center;
            padding: 40px;
        }
        h1 {
            font-size: 24px;
            color: #fff1c1;
            text-shadow: 2px 2px #000;
        }
        .panel {
            background-color: rgba(0, 0, 0, 0.7);
            border: 4px solid #d4a24b;
            padding: 20px;
            max-width: 700px;
            margin: 0 auto 30px;
            border-radius: 10px;
        }
        .beer-area {
            position: relative;
            height: 220px;
            margin-bottom: 20px;
        }
        .tap {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            top: 0;
            width: 100px;
        }
        .glass {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            bottom: 0;
            width: 80px;
            transition: transform 1s ease-out, opacity 1s ease-out;
        }
        .bubble {
            position: absolute;
            bottom: 40px;
            left: 50%;
            width: 8px;
            height: 8px;
            background: #fff;
            border-radius: 50%;
            opacity: 0;
            animation: bubble 1s ease-out forwards;
        }
        @keyframes bubble {
            0% { bottom: 40px; opacity: 0; }
            50% { opacity: 1; }
            100% { bottom: 120px; opacity: 0; }
        }
        .foam {
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 90px;
            height: 20px;
            background: #fffbe0;
            border-radius: 10px;
            display: none;
        }
        .foam.show {
            display: block;
            animation: foamExpand 0.5s ease-out;
        }
        @keyframes foamExpand {
            from { transform: translateX(-50%) scale(0); }
            to { transform: translateX(-50%) scale(1); }
        }
        .slide-out {
            transform: translateX(150%) translateY(-50px);
            opacity: 0;
        }
        .btn-main {
            background-color: #d4a24b;
            color: #000;
            padding: 20px 40px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            border-radius: 8px;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #d4a24b;
        }
    </style>
    <script>
        function triggerGlassAnimation() {
            const glass = document.getElementById('beer-glass');
            const foam = document.getElementById('foam');
            const beerArea = document.querySelector('.beer-area');

            glass.src = 'https://i.imgur.com/zsSbWZK.png'; // full beer
            foam.classList.add('show');

            for (let i = 0; i < 5; i++) {
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.style.left = (45 + Math.random() * 10) + '%';
                beerArea.appendChild(bubble);
                setTimeout(() => beerArea.removeChild(bubble), 1000);
            }

            setTimeout(() => {
                glass.classList.add('slide-out');
            }, 500);

            setTimeout(() => {
                glass.classList.remove('slide-out');
                foam.classList.remove('show');
                glass.src = 'https://i.imgur.com/7uOlgPA.png'; // empty beer
            }, 2000);
        }
    </script>
</head>
<body>
    <h1>🍺 1 MILLION BEERS 🍺</h1>
    <div class="panel">
        <div class="beer-area">
            <img class="tap" src="https://i.imgur.com/Ft4Qv4h.png" alt="Tap">
            <div id="foam" class="foam"></div>
            <img id="beer-glass" class="glass" src="https://i.imgur.com/7uOlgPA.png" alt="Beer Glass">
        </div>
        <form action="/add/Daniel/1" method="post" onsubmit="triggerGlassAnimation()">
            <button class="btn-main" type="submit">+1 BEER</button>
        </form>
        <div style="margin-top: 15px; font-size: 14px; color: #fff">Total Beers Consumed: {{ grand_total }}</div>
    </div>

    <div class="panel">
        <h2>Top Drinkers This Week</h2>
        <table>
            <tr><th>Rank</th><th>Name</th><th>Beers</th></tr>
            {% for row in weekly %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>
                    {{ row[0] }}
                    {% if loop.index <= 5 and row[1] > 0 %}<br><small><em>{{ titles[loop.index0] }}</em></small>{% endif %}
                    {% if row[1] == 0 %}<br><small><em>Virgin</em></small>{% endif %}
                </td>
                <td>{{ row[1] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)