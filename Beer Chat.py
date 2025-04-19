from flask import Flask, render_template_string, request, redirect, url_for, jsonify
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
        timestamp = datetime.fromisoformat(entry['timestamp'])
        if time_filter == 'week' and now - timestamp > timedelta(days=7):
            continue
        elif time_filter == 'month' and now - timestamp > timedelta(days=30):
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

@app.route('/data')
def data_api():
    data = load_data()
    total = build_ranking(count_beers(data))
    weekly = build_ranking(count_beers(data, 'week'))
    monthly = build_ranking(count_beers(data, 'month'))
    return jsonify({
        'total': total,
        'weekly': weekly,
        'monthly': monthly
    })

@app.route('/add/<name>/<int:amount>', methods=['POST'])
def add_beer(name, amount):
    if name in FRIENDS:
        data = load_data()
        for _ in range(amount):
            data.append({"name": name, "timestamp": datetime.now().isoformat()})
        save_data(data)
    return redirect(url_for('leaderboard'))

TEMPLATE = '''
<!-- Your full working HTML layout should be pasted here -->
<!-- Add JavaScript like this to fetch data every 5 seconds -->
<script>
    function fetchLeaderboard() {
        fetch('/data')
            .then(res => res.json())
            .then(data => {
                // TODO: Update DOM with data.total / data.weekly / data.monthly
                console.log(data); // Example: just log for now
            });
    }
    setInterval(fetchLeaderboard, 5000); // Refresh every 5 seconds
</script>
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
