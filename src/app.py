from flask import Flask, render_template, jsonify, request
from chart_data_store import ChartDataStore
from storyline_data_store import StorylineDataStore
from flask_cors import CORS
import os

app = Flask(__name__)
data_store = ChartDataStore()
storyline_store = StorylineDataStore()

# Enable CORS for the app
CORS(app)

#############################################
##           Storyline Functions
#############################################
# API endpoint to get all storyline nodes
@app.route('/api/storyline', methods=['GET'])
def get_storyline_nodes():
    nodes = storyline_store.get_storyline_nodes()
    nodes_list = list(nodes.values())[::-1]
    return jsonify(nodes_list)

# API endpoint to add a new storyline node
@app.route('/api/storyline', methods=['POST'])
def add_storyline_node():
    new_node_data = request.json
    node = storyline_store.add_storyline_node(new_node_data)
    return jsonify(node), 201

# API endpoint to get a single storyline node
@app.route('/api/storyline/<node_id>', methods=['GET'])
def get_storyline_node(node_id):
    node = storyline_store.get_storyline_node(node_id)
    if node:
        return jsonify(node)
    else:
        return jsonify({"error": "Node not found"}), 404

# API endpoint to update an existing storyline node
@app.route('/api/storyline/<node_id>', methods=['PUT'])
def update_storyline_node(node_id):
    updated_data = request.json
    node = storyline_store.update_storyline_node(node_id, updated_data)
    if node:
        return jsonify(node)
    else:
        return jsonify({"error": "Node not found"}), 404

# API endpoint to delete a storyline node
@app.route('/api/storyline/<node_id>', methods=['DELETE'])
def delete_storyline_node(node_id):
    success = storyline_store.delete_storyline_node(node_id)
    if success:
        return jsonify({"message": "Node deleted successfully"})
    else:
        return jsonify({"error": "Node not found"}), 404

# --- Header/Footer API ---
@app.route('/api/header_footer', methods=['GET'])
def get_header_footer_api():
    return jsonify(storyline_store.get_header_footer())

@app.route('/api/header_footer', methods=['POST'])
def save_header_footer_api():
    data = request.get_json()
    if not data:
        return jsonify(success=False, error='No data received'), 400
    storyline_store.set_header_footer(data)
    return jsonify(success=True)

#############################################
##                  Dashboard Functions
#############################################

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

#############################################
##                  Main Entry Functions
#############################################

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
