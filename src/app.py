
from flask import Flask, render_template, jsonify, request
from chart_data_store import ChartDataStore
from flask_cors import CORS
import uuid
import os
import json


app = Flask(__name__)
data_store = ChartDataStore()

# File paths for persistent storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEADER_FOOTER_PATH = os.path.join(BASE_DIR, 'header_footer.json')
TIMELINE_NODES_PATH = os.path.join(BASE_DIR, 'timeline_nodes.json')

# Enable CORS for the app
CORS(app)


# Persistent storage helpers
def load_timeline_nodes():
    if os.path.exists(TIMELINE_NODES_PATH):
        with open(TIMELINE_NODES_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_timeline_nodes(nodes):
    with open(TIMELINE_NODES_PATH, 'w') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

def load_header_footer():
    if os.path.exists(HEADER_FOOTER_PATH):
        with open(HEADER_FOOTER_PATH, 'r') as f:
            return json.load(f)
    return {
        "header": {
            "main_title": "THE LOVE STORY",
            "subtitle": "A Journey Through Time for you or what you love",
        },
        "footer": {
            "footer_text": "© 2024 The love Company. All rights reserved."
        }
    }

def save_header_footer(data):
    with open(HEADER_FOOTER_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

timeline_nodes = load_timeline_nodes()


# API endpoint to get all timeline nodes
@app.route('/api/timeline', methods=['GET'])
def get_nodes():
    global timeline_nodes
    timeline_nodes = load_timeline_nodes()
    # Sort by insertion order, latest first (assuming dict preserves order)
    nodes_list = list(timeline_nodes.values())[::-1]
    return jsonify(nodes_list)


# API endpoint to add a new timeline node
@app.route('/api/timeline', methods=['POST'])
def add_node():
    global timeline_nodes
    timeline_nodes = load_timeline_nodes()
    new_node_data = request.json
    new_node_id = str(uuid.uuid4())
    new_node_data['id'] = new_node_id
    timeline_nodes[new_node_id] = new_node_data
    save_timeline_nodes(timeline_nodes)
    return jsonify(new_node_data), 201


# API endpoint to update an existing timeline node

@app.route('/api/timeline/<node_id>', methods=['GET'])
def get_node(node_id):
    timeline_nodes = load_timeline_nodes()
    node = timeline_nodes.get(node_id)
    if node:
        return jsonify(node)
    else:
        return jsonify({"error": "Node not found"}), 404

@app.route('/api/timeline/<node_id>', methods=['PUT'])
def update_node(node_id):
    timeline_nodes = load_timeline_nodes()
    if node_id not in timeline_nodes:
        return jsonify({"error": "Node not found"}), 404
    updated_data = request.json
    timeline_nodes[node_id].update(updated_data)
    save_timeline_nodes(timeline_nodes)
    return jsonify(timeline_nodes[node_id])

# API endpoint to delete a timeline node
@app.route('/api/timeline/<node_id>', methods=['DELETE'])
def delete_node(node_id):
    timeline_nodes = load_timeline_nodes()
    if node_id not in timeline_nodes:
        return jsonify({"error": "Node not found"}), 404
    del timeline_nodes[node_id]
    save_timeline_nodes(timeline_nodes)
    return jsonify({"message": "Node deleted successfully"})



# --- Header/Footer API ---
@app.route('/api/header_footer', methods=['GET'])
def get_header_footer():
    return jsonify(load_header_footer())

@app.route('/api/header_footer', methods=['POST'])
def save_header_footer_api():
    data = request.get_json()
    if not data:
        return jsonify(success=False, error='No data received'), 400
    save_header_footer(data)
    return jsonify(success=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    data = data_store.load_static_data()
    realtime_data = data_store.load_realtime_data()
    return render_template('dashboard.html', chart_data=data, realtime_data=realtime_data)

# Add endpoint for saving static data
@app.route('/add_static_data', methods=['POST'])
def add_static_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify(success=False, error='No data received'), 400
        data_store.save_static_data(data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
