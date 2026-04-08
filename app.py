from flask import Flask, render_template, request, jsonify
import hashlib
import json
import time
import math

app = Flask(__name__)

# ============================================================================
# LEDGER MANAGEMENT
# ============================================================================

# Load ledger from persistent storage
try:
    with open("ledger.json", "r") as f:
        ledger = json.load(f)
except:
    ledger = []


def save_ledger():
    """Save ledger to JSON file"""
    with open("ledger.json", "w") as f:
        json.dump(ledger, f, indent=4)


def create_hash(data):
    """Generate SHA256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


# ============================================================================
# ADVANCED TRUST SCORING SYSTEM
# ============================================================================

SOURCE_WEIGHTS = {
    "government": 1.0,
    "gov": 1.0,
    "private": 0.8,
    "academic": 0.9,
    "unknown": 0.5
}


def calculate_source_reliability_score(source):
    """
    Calculate source reliability: government > academic > private > unknown
    Returns 0-100 points
    """
    normalized_source = source.lower().strip()
    weight = SOURCE_WEIGHTS.get(normalized_source, 0.5)
    return int(weight * 100)


def calculate_edit_penalty(edits):
    """
    Penalty for number of edits (data integrity concern)
    More edits = less trustworthy
    Returns penalty: 0-40 points
    """
    return min(edits * 5, 40)


def calculate_time_decay(timestamp_str):
    """
    Apply time decay: older data is slightly less trusted
    Data more than 30 days old gets 5% penalty
    Returns penalty: 0-5 points
    """
    try:
        block_time = float(timestamp_str)
        current_time = time.time()
        days_old = (current_time - block_time) / (86400)
        
        if days_old > 30:
            return 5
        elif days_old > 7:
            return 2
        return 0
    except:
        return 0


def simulate_anomaly_detection(name, source, edits):
    """
    Simulated anomaly detection (for demonstration)
    Detects unusual patterns: high edits, unusual names, unknown sources
    Returns penalty: 0-10 points
    """
    penalty = 0
    
    # High edit count anomaly
    if edits > 10:
        penalty += 5
    
    # Unknown source with high edits is suspicious
    if source.lower() == "unknown" and edits > 5:
        penalty += 5
    
    return min(penalty, 10)


def calculate_trust_score(source, edits, timestamp=None):
    """
    Multi-factor trust score calculation (0-100)
    
    Factors:
    1. Source reliability (0-100)
    2. Edit penalty (0-40)
    3. Time decay (0-5)
    4. Anomaly detection (0-10)
    """
    source_score = calculate_source_reliability_score(source)
    
    # Apply penalties
    edit_penalty = calculate_edit_penalty(edits)
    time_penalty = 0 if timestamp is None else calculate_time_decay(timestamp)
    
    # Calculate final score
    final_score = source_score - edit_penalty - time_penalty
    return max(min(final_score, 100), 0)


def get_risk_level(trust_score):
    """
    Classify risk level based on trust score
    """
    if trust_score >= 75:
        return "Low"
    elif trust_score >= 50:
        return "Medium"
    else:
        return "High"


def calculate_enhanced_trust_metrics(block_data, timestamp):
    """
    Calculate enhanced trust metrics including anomaly detection
    """
    source = block_data.get('source', 'unknown')
    edits = block_data.get('edits', 0)
    name = block_data.get('dataset', '')
    
    trust_score = calculate_trust_score(source, edits, timestamp)
    anomaly_penalty = simulate_anomaly_detection(name, source, edits)
    trust_score -= anomaly_penalty
    trust_score = max(min(trust_score, 100), 0)
    
    risk_level = get_risk_level(trust_score)
    
    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "anomaly_detected": anomaly_penalty > 0
    }


# ============================================================================
# BLOCKCHAIN OPERATIONS
# ============================================================================

def add_block(data):
    """Add a new block to the ledger (blockchain style)"""
    prev_hash = ledger[-1]['hash'] if ledger else "0"
    timestamp = str(time.time())
    
    # Create block hash
    block_content = json.dumps(data, sort_keys=True) + prev_hash + timestamp
    block_hash = create_hash(block_content)
    
    # Calculate trust metrics
    metrics = calculate_enhanced_trust_metrics(data, timestamp)
    data.update(metrics)
    
    # Create block
    block = {
        "data": data,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "hash": block_hash
    }
    
    ledger.append(block)
    save_ledger()
    
    return block


def verify_block_integrity(block_index):
    """
    Verify if a block's hash is valid (tamper detection)
    Recalculates hash and compares with stored hash
    """
    if block_index < 0 or block_index >= len(ledger):
        return {"valid": False, "message": "Block not found"}
    
    block = ledger[block_index]
    
    # Recalculate hash
    block_content = json.dumps(block['data'], sort_keys=True) + block['prev_hash'] + block['timestamp']
    recalculated_hash = create_hash(block_content)
    
    is_valid = recalculated_hash == block['hash']
    
    return {
        "valid": is_valid,
        "message": "Valid ✓" if is_valid else "Tampered ✗",
        "stored_hash": block['hash'],
        "calculated_hash": recalculated_hash
    }


def verify_chain_integrity():
    """
    Verify entire chain integrity by checking all hashes
    """
    if not ledger:
        return {"valid": True, "message": "Ledger is empty"}
    
    for i in range(len(ledger)):
        current_block = ledger[i]
        
        # Check previous hash link
        if i > 0:
            prev_block = ledger[i - 1]
            if current_block['prev_hash'] != prev_block['hash']:
                return {
                    "valid": False,
                    "message": f"Chain broken at block {i}",
                    "broken_at": i
                }
        else:
            # First block should reference "0"
            if current_block['prev_hash'] != "0":
                return {
                    "valid": False,
                    "message": "Genesis block invalid"
                }
        
        # Verify block hash
        result = verify_block_integrity(i)
        if not result['valid']:
            return {
                "valid": False,
                "message": f"Block {i} hash is invalid (tampered)",
                "tampered_block": i
            }
    
    return {"valid": True, "message": "Chain integrity verified ✓"}


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    """Render dashboard"""
    return render_template("index.html", ledger=ledger)


@app.route('/api/ledger', methods=['GET'])
def get_ledger():
    """Get full ledger data"""
    return jsonify(ledger)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get ledger statistics for dashboard"""
    if not ledger:
        return jsonify({
            "total_blocks": 0,
            "avg_trust_score": 0,
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0}
        })
    
    trust_scores = [block['data'].get('trust_score', 0) for block in ledger]
    risk_levels = [block['data'].get('risk_level', 'Unknown') for block in ledger]
    
    risk_distribution = {
        "Low": risk_levels.count("Low"),
        "Medium": risk_levels.count("Medium"),
        "High": risk_levels.count("High")
    }
    
    return jsonify({
        "total_blocks": len(ledger),
        "avg_trust_score": round(sum(trust_scores) / len(trust_scores), 2),
        "risk_distribution": risk_distribution
    })


@app.route('/add', methods=['POST'])
def add_dataset():
    """Add new dataset to ledger"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({"error": "Dataset name required"}), 400
    
    block_data = {
        "dataset": data.get('name', ''),
        "source": data.get('source', 'unknown'),
        "edits": int(data.get('edits', 0))
    }
    
    block = add_block(block_data)
    
    return jsonify({
        "message": "Dataset added successfully!",
        "trust_score": block['data'].get('trust_score'),
        "risk_level": block['data'].get('risk_level')
    })


@app.route('/verify/<int:block_index>', methods=['GET'])
def verify_integrity(block_index):
    """Verify integrity of a specific block"""
    return jsonify(verify_block_integrity(block_index))


@app.route('/verify-chain', methods=['GET'])
def verify_full_chain():
    """Verify entire chain integrity"""
    return jsonify(verify_chain_integrity())


@app.route('/search', methods=['GET'])
def search_datasets():
    """Search datasets by name"""
    query = request.args.get('q', '').lower()
    
    results = [
        {
            "index": i,
            "data": block['data'],
            "timestamp": block['timestamp'],
            "hash": block['hash']
        }
        for i, block in enumerate(ledger)
        if query in block['data'].get('dataset', '').lower()
    ]
    
    return jsonify(results)


@app.route('/filter', methods=['GET'])
def filter_by_risk():
    """Filter datasets by risk level"""
    risk = request.args.get('risk', '').capitalize()
    
    results = [
        {
            "index": i,
            "data": block['data'],
            "timestamp": block['timestamp'],
            "hash": block['hash']
        }
        for i, block in enumerate(ledger)
        if block['data'].get('risk_level') == risk
    ]
    
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)