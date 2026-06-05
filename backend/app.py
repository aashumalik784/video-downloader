from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "URL missing"}), 400
    
    # Naya Active Endpoint
    api_url = "https://cobalt.api.pages.dev/api/json"
    payload = {"url": video_url}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
