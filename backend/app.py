from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

def extract_video_url(data):
    """Har type ke response structure se video URL nikalega"""
    
    # Direct keys
    if isinstance(data, dict):
        direct_keys = ['video_url', 'url', 'download_url', 'link', 'hd', 'sd']
        for key in direct_keys:
            if key in data and data[key]:
                return data[key]
        
        # Nested result mein dekho
        if 'result' in data and isinstance(data['result'], dict):
            for key in direct_keys:
                if key in data['result'] and data['result'][key]:
                    return data['result'][key]
        
        # Media array mein dekho
        if 'medias' in data and isinstance(data['medias'], list):
            for media in data['medias']:
                if isinstance(media, dict):
                    for key in ['url', 'video_url', 'link']:
                        if key in media and media[key]:
                            return media[key]
        
        # RapidAPI ka common pattern
        if 'data' in data and isinstance(data['data'], dict):
            return extract_video_url(data['data'])
    
    return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    
    if not video_url:
        return jsonify({"error": "URL do bhai"}), 400
    
    # RapidAPI ka active endpoint
    url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    payload = {"url": video_url}
    headers = {
        "x-rapidapi-key": "45ceb2f534msh34e98d782a09e76p11792ejsnd963d248c5c1",
        "x-rapidapi-host": "auto-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response_data = response.json()
        
        # Smart link extraction
        video_link = extract_video_url(response_data)
        
        if video_link:
            return jsonify({
                "success": True,
                "video_url": video_link,
                "original_response": response_data  # debugging ke liye
            })
        else:
            return jsonify({
                "success": False,
                "error": "Video link nahi mila",
                "full_response": response_data  # exact response dikhao
            }), 404
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ Social Media Downloader API Active!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
