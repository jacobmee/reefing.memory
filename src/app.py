from flask import Flask, render_template, jsonify, request
from data_store import ChartDataStore
from data_store import StoryDataStore
from data_store import SummaryDataStore
from flask_cors import CORS
from common import logger
import os

app = Flask(__name__)
chart_store = ChartDataStore()
summary_store = SummaryDataStore()

# Enable CORS for the app
CORS(app)

#############################################
##           Summary Functions
#############################################
# Get all summary items
@app.route("/api/summary", methods=["GET"])
def get_summary_items():
    items = summary_store.get_summary_nodes()
    return jsonify(items)

# Add a summary item (with image upload)
@app.route("/api/summary", methods=["POST"])
def add_summary_item():
    new_item_data = request.json
    item = summary_store.add_summary_node(new_item_data)
    return jsonify(item), 201

@app.route('/api/summary/order', methods=['POST'])
def set_summary_order():
    data = request.get_json()
    order_list = data.get('order', [])
    if not isinstance(order_list, list):
        return jsonify({'error': 'Invalid order format'}), 400
    try:
        from app import summary_store  # 或根据你的实际导入
        summary_store.set_summary_order(order_list)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# API endpoint to update an existing summary item
@app.route("/api/summary/<item_id>", methods=["PUT"])
def update_summary_item(item_id):
    updated_data = request.json
    item = summary_store.update_summary_node(item_id, updated_data)
    if item:
        return jsonify(item)
    else:
        return jsonify({"error": "Node not found"}), 404


# API endpoint to delete a summary item
@app.route("/api/summary/<item_id>", methods=["DELETE"])
def delete_summary_item(item_id):
    success = summary_store.delete_summary_node(item_id)
    if success:
        return jsonify({"message": "Item deleted successfully"})
    else:
        return jsonify({"error": "Item not found"}), 404


# Update info
@app.route("/api/summary/info", methods=["POST"])
def save_summary_info():
    data = request.get_json()
    if not data:
        return jsonify(success=False, error="No data received"), 400
    summary_store.set_info(data)
    return jsonify(success=True)


@app.route("/api/summary/info", methods=["GET"])
def get_summary_info():
    return jsonify(summary_store.get_info())


#############################################
##           Story Functions
#############################################
# API endpoint to get all story nodes
@app.route("/story")
def story():
    return render_template("story.html")

@app.route("/api/story", methods=["GET"])
def get_story_nodes():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    nodes = store.get_story_nodes()
    nodes_list = list(nodes.values())[::-1]
    return jsonify(nodes_list)


# API endpoint to add a new story node
@app.route("/api/story", methods=["POST"])
def add_story_node():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    new_node_data = request.json
    node = store.add_story_node(new_node_data)
    return jsonify(node), 201


# API endpoint to get a single story node
@app.route("/api/story/<node_id>", methods=["GET"])
def get_story_node(node_id):
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    node = store.get_story_node(node_id)
    if node:
        return jsonify(node)
    else:
        return jsonify({"error": "Node not found"}), 404


# API endpoint to update an existing story node
@app.route("/api/story/<node_id>", methods=["PUT"])
def update_story_node(node_id):
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    updated_data = request.json
    node = store.update_story_node(node_id, updated_data)
    if node:
        return jsonify(node)
    else:
        return jsonify({"error": "Node not found"}), 404


# API endpoint to delete a story node
@app.route("/api/story/<node_id>", methods=["DELETE"])
def delete_story_node(node_id):
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    success = store.delete_story_node(node_id)
    if success:
        return jsonify({"message": "Node deleted successfully"})
    else:
        return jsonify({"error": "Node not found"}), 404


@app.route("/api/story/info", methods=["GET"])
def get_info():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = StoryDataStore(uuid)
    return jsonify(store.get_info())


@app.route("/api/story/info", methods=["POST"])
def save_info():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify(success=False, error="Missing uuid"), 400
    store = StoryDataStore(uuid)
    data = request.get_json()
    if not data:
        return jsonify(success=False, error="No data received"), 400
    store.set_info(data)
    return jsonify(success=True)


#############################################
##                  Dashboard Functions
#############################################
@app.route("/dashboard")
def dashboard():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify(success=False, error="Missing uuid"), 400
    store = ChartDataStore(uuid)
    data = store.load_static_data()
    realtime_data = store.load_realtime_data()
    return render_template(
        "dashboard.html", chart_data=data, realtime_data=realtime_data
    )

# API endpoint for chart data (for radar chart in story.html)
@app.route("/dashboard/mini", methods=["GET"])
def get_chart_data():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = ChartDataStore(uuid)
    data = store.load_static_data()
    # 只返回最后一条数据
    if isinstance(data, list) and data:
        return jsonify(data[-1])
    return jsonify({})

# Add endpoint for saving static data
@app.route("/dashboard", methods=["POST"])
def add_static_data():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify(success=False, error="Missing uuid"), 400
    store = ChartDataStore(uuid) 
    try:
        data = request.get_json()
        if not data:
            return jsonify(success=False, error="No data received"), 400
        store.save_static_data(data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route("/dashboard/info", methods=["POST"])
def add_info_data():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify(success=False, error="Missing uuid"), 400
    store = ChartDataStore(uuid) 
    try:
        data = request.get_json()
        if not data:
            return jsonify(success=False, error="No data received"), 400
        store.set_dashboard_info(data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route("/dashboard/info", methods=["GET"])
def get_info_data():
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    store = ChartDataStore(uuid)
    data = store.get_dashboard_info()
    if data:
        return jsonify(data)
    return jsonify({})

#############################################
##                  Main Entry Functions
#############################################

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003, host="0.0.0.0")
