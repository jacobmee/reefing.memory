
from flask import Flask, render_template, jsonify, request
from chart_data_store import ChartDataStore

app = Flask(__name__)
data_store = ChartDataStore()

@app.route('/')
def index():
    data = data_store.load_static_data()
    realtime_data = data_store.load_realtime_data()
    return render_template('index.html', chart_data=data, realtime_data=realtime_data)


if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
