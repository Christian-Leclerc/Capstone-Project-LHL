from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def mockup_data():
    print("Inside /api/data route")
    return jsonify({"status": "success", "data": "mockup_data_here"})

@app.route('/recommend', methods=['POST'])
def recommend():
    # Mock data for testing
    recs = {'listing1': '300k', 'listing2': '400k', 'listing3': '500k'}
    return jsonify(recs)