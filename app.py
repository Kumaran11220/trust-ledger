from flask import Flask, render_template, request, jsonify
import hashlib
import json
import time

def generate_data_hash(name, source, edits):
    raw = f"{name}-{source}-{edits}"
    return hashlib.sha256(raw.encode()).hexdigest()

app = Flask(__name__)

# Load ledger
try:
    with open("ledger.json", "r") as f:
        ledger = json.load(f)
except:
    ledger = []

def create_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def add_block(data):
    prev_hash = ledger[-1]['hash'] if ledger else "0"
    timestamp = str(time.time())

    block_data = json.dumps(data) + prev_hash + timestamp
    block_hash = create_hash(block_data)

    block = {
        "data": data,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "hash": block_hash
    }

    ledger.append(block)

    with open("ledger.json", "w") as f:
        json.dump(ledger, f, indent=4)

def calculate_trust_score(source, edits):
    score = 100
    if source == "unknown":
        score -= 30
    elif source == "private":
        score -= 10
    score -= edits * 5
    return max(score, 0)

@app.route('/')
def home():
    return render_template("index.html", ledger=ledger)

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    trust = calculate_trust_score(data['source'], data['edits'])
    data_hash = generate_data_hash(data['name'], data['source'], data['edits'])

    block_data = {
        "dataset": data['name'],
        "source": data['source'],
        "edits": data['edits'],
        "trust_score": trust,
        "hash_id": data_hash
    }

    add_block(block_data)
    return jsonify({"message": "Added!", "trust_score": trust})

if __name__ == "__main__":
    app.run(debug=True)