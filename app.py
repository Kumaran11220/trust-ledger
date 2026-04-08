from flask import Flask, render_template, request, jsonify
import hashlib
import json
import os
import time

app = Flask(__name__)
LEDGER_PATH = 'ledger.json'

SOURCE_REPUTATION = {
    'government': 1.0,
    'gov': 1.0,
    'verified_org': 0.9,
    'academic': 0.85,
    'research': 0.8,
    'private': 0.65,
    'commercial': 0.6,
    'unknown': 0.4,
    'unverified': 0.3
}

CONSENSUS_LABELS = {
    1: {'symbol': '✖', 'message': 'Weak Consensus', 'strength': 'Weak'},
    2: {'symbol': '⚠', 'message': 'Moderate Consensus', 'strength': 'Moderate'},
    3: {'symbol': '✔', 'message': 'Strong Consensus', 'strength': 'Strong'}
}


def load_ledger():
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


ledger = load_ledger()


def save_ledger():
    with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=4)


def normalize_dataset(dataset_name):
    return dataset_name.strip().lower()


def normalize_source(source):
    return source.strip().lower()


def source_weight(source):
    """Return reliability weight for a source used in weighted cross-verification."""
    weights = {
        'government': 1.0,
        'gov': 1.0,
        'verified_org': 0.8,
        'private': 0.6,
        'unknown': 0.2
    }
    return weights.get(normalize_source(source), weights['unknown'])


def reputation_score(source):
    return SOURCE_REPUTATION.get(normalize_source(source), SOURCE_REPUTATION['unknown'])


def source_score(source):
    """Convert a source reputation into a base trust score."""
    return reputation_score(source) * 55 + 20


def verification_count(dataset_name):
    normalized = normalize_dataset(dataset_name)
    sources = {
        normalize_source(block.get('data', {}).get('source', 'unknown'))
        for block in ledger
        if normalize_dataset(block.get('data', {}).get('dataset', '')) == normalized
    }
    return len(sources)


def cross_verify(dataset_name):
    """Compute a weighted consensus score from unique dataset sources."""
    normalized = normalize_dataset(dataset_name)
    unique_sources = {
        normalize_source(block.get('data', {}).get('source', 'unknown'))
        for block in ledger
        if normalize_dataset(block.get('data', {}).get('dataset', '')) == normalized
    }
    total_weight = sum(source_weight(source) for source in unique_sources)

    if total_weight >= 2.0:
        return 40
    if total_weight >= 1.2:
        return 25
    return 10


def calculate_trust_score(source, dataset_name):
    score = source_score(source) + cross_verify(dataset_name)
    return min(100, int(score))


def calculate_risk_level(count):
    if count >= 3:
        return 'LOW'
    if count == 2:
        return 'MEDIUM'
    return 'HIGH'


def consensus_data(count):
    if count >= 3:
        return CONSENSUS_LABELS[3]
    if count == 2:
        return CONSENSUS_LABELS[2]
    return CONSENSUS_LABELS[1]


def create_hash(dataset, source, timestamp, prev_hash):
    content = json.dumps({
        'dataset': dataset,
        'source': source,
        'timestamp': timestamp,
        'prev_hash': prev_hash
    }, sort_keys=True)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def refresh_dataset_blocks(dataset_name):
    count = verification_count(dataset_name)
    for block in ledger:
        if normalize_dataset(block.get('data', {}).get('dataset', '')) == normalize_dataset(dataset_name):
            source = block['data'].get('source', 'unknown')
            block['data']['verification_count'] = count
            block['data']['trust_score'] = calculate_trust_score(source, dataset_name)
            block['data']['risk_level'] = calculate_risk_level(count)
            consensus = consensus_data(count)
            block['data']['consensus_level'] = consensus['strength']
            block['data']['consensus_message'] = consensus['message']
    save_ledger()


def add_block(dataset, source):
    prev_hash = ledger[-1]['hash'] if ledger else '0'
    timestamp = str(time.time())
    block_hash = create_hash(dataset, source, timestamp, prev_hash)

    block = {
        'data': {
            'dataset': dataset,
            'source': source,
            'verification_count': 1,
            'trust_score': 0,
            'risk_level': 'HIGH',
            'consensus_level': 'Weak',
            'consensus_message': 'Weak Consensus'
        },
        'timestamp': timestamp,
        'prev_hash': prev_hash,
        'hash': block_hash,
        'block_height': len(ledger)
    }

    ledger.append(block)
    refresh_dataset_blocks(dataset)
    return block


def verify_block_integrity(index):
    if index < 0 or index >= len(ledger):
        return {'valid': False, 'message': 'Block not found'}

    block = ledger[index]
    data = block.get('data', {})
    expected_hash = create_hash(data.get('dataset', ''), data.get('source', ''), block.get('timestamp', ''), block.get('prev_hash', ''))
    valid = expected_hash == block.get('hash')
    return {
        'valid': valid,
        'message': 'Integrity intact' if valid else 'Integrity compromised',
        'stored_hash': block.get('hash'),
        'calculated_hash': expected_hash,
        'block_height': index
    }


def verify_chain():
    if not ledger:
        return {'valid': True, 'message': 'Ledger is empty'}

    for i, block in enumerate(ledger):
        if i > 0 and block.get('prev_hash') != ledger[i - 1].get('hash'):
            return {'valid': False, 'message': f'Chain broken at block {i}'}
        integrity = verify_block_integrity(i)
        if not integrity['valid']:
            return {'valid': False, 'message': f'Block {i} invalid'}

    return {'valid': True, 'message': 'Chain integrity verified'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/ledger', methods=['GET'])
def api_ledger():
    return jsonify(ledger)


@app.route('/api/stats', methods=['GET'])
def api_stats():
    if not ledger:
        return jsonify({'total_blocks': 0, 'avg_trust_score': 0, 'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}})
    trust_scores = [block['data']['trust_score'] for block in ledger]
    risk_levels = [block['data']['risk_level'] for block in ledger]
    return jsonify({'total_blocks': len(ledger), 'avg_trust_score': round(sum(trust_scores) / len(trust_scores), 2), 'risk_distribution': {'LOW': risk_levels.count('LOW'), 'MEDIUM': risk_levels.count('MEDIUM'), 'HIGH': risk_levels.count('HIGH')}})


@app.route('/add', methods=['POST'])
def api_add():
    payload = request.json or {}
    dataset = payload.get('name', '').strip()
    source = normalize_source(payload.get('source', 'unknown'))
    if not dataset:
        return jsonify({'error': 'Dataset name is required.'}), 400
    if source not in SOURCE_REPUTATION:
        source = 'unknown'
    block = add_block(dataset, source)
    return jsonify({'message': 'Dataset registered.', 'trust_score': block['data']['trust_score'], 'risk_level': block['data']['risk_level'], 'verification_count': block['data']['verification_count'], 'consensus_message': block['data']['consensus_message']})


@app.route('/search', methods=['GET'])
def api_search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify(ledger)
    return jsonify([block for block in ledger if query in block['data'].get('dataset', '').lower()])


@app.route('/filter', methods=['GET'])
def api_filter():
    risk = request.args.get('risk', '').strip().upper()
    if not risk:
        return jsonify(ledger)
    return jsonify([block for block in ledger if block['data'].get('risk_level', '').upper() == risk])


@app.route('/verify/<int:index>', methods=['GET'])
def api_verify(index):
    return jsonify(verify_block_integrity(index))


@app.route('/verify-chain', methods=['GET'])
def api_verify_chain():
    return jsonify(verify_chain())


@app.route('/verify-consensus/<int:index>', methods=['GET'])
def api_verify_consensus(index):
    if index < 0 or index >= len(ledger):
        return jsonify({'error': 'Block not found'}), 404
    data = ledger[index]['data']
    return jsonify({'verification_count': data['verification_count'], 'consensus_message': data['consensus_message'], 'symbol': data['consensus_level']})


if __name__ == '__main__':
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(debug=False)
