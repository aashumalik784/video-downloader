from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def find_url(data):
    # Har tarah ke JSON structure se URL nikalne wala smart logic
    keys = ['video_url', 'url', 'download_url', 'link', 'hd', 'sd', 'media']
    if isinstance(data, dict):
        for k in keys:
            if k in data and data[k]: return data[k]
        if 'result' in data: return find_url(data['result'])
        if 'data' in data: return find_url(data['data'])
    return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    if not video_url: return jsonify({"error": "URL missing"}), 400
    
    url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    headers = {
        "x-rapidapi-key": "45ceb2f534msh34e98d782a09e76p11792ejsnd963d248c5c1",
        "x-rapidapi-host": "auto-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(url, json={"url": video_url}, headers=headers, timeout=15)
        res_data = res.json()
        final_link = find_url(res_data)
        
        if final_link:
            return jsonify({"success": True, "video_url": final_link})
        return jsonify({"success": False, "error": "Link not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
