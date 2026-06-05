from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

def extract_video_url(data):
    """Smart video URL extractor"""
    if isinstance(data, dict):
        direct_keys = ['video_url', 'url', 'download_url', 'link', 'hd', 'sd', 'video']
        for key in direct_keys:
            if key in data and data[key]:
                return data[key]
        
        if 'result' in data and isinstance(data['result'], dict):
            return extract_video_url(data['result'])
        
        if 'data' in data and isinstance(data['data'], dict):
            return extract_video_url(data['data'])
    
    return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    
    if not video_url:
        return jsonify({"error": "URL do bhai"}), 400
    
    # Multiple API endpoints with fallback
    apis = [
        {
            "url": "https://instagram-video-downloader-download-instagram-videos-stories1.p.rapidapi.com/get",
            "headers": {
                "x-rapidapi-key": "45ceb2f534msh34e98d782a09e76p11792ejsnd963d248c5c1",
                "x-rapidapi-host": "instagram-video-downloader-download-instagram-videos-stories1.p.rapidapi.com"
            },
            "params": {"url": video_url}
        },
        {
            "url": "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/convert",
            "headers": {
                "x-rapidapi-key": "45ceb2f534msh34e98d782a09e76p11792ejsnd963d248c5c1",
                "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
            },
            "params": {"url": video_url}
        }
    ]
    
    # Try each API
    for api in apis:
        try:
            response = requests.get(api["url"], headers=api["headers"], params=api["params"], timeout=15)
            data = response.json()
            
            video_link = extract_video_url(data)
            if video_link:
                return jsonify({
                    "success": True,
                    "video_url": video_link,
                    "source": "RapidAPI"
                })
        except:
            continue
    
    # Fallback: Direct video extraction using yt-dlp like service
    try:
        # Using a free public API as last resort
        fallback_url = f"https://p.oceansaver.in/ajax/download.php?url={video_url}"
        response = requests.get(fallback_url, timeout=10)
        if response.status_code == 200:
            # Extract video link from response
            match = re.search(r'(https?://[^\s"\'<>]+\.(mp4|mov|avi|mkv))', response.text)
            if match:
                return jsonify({
                    "success": True,
                    "video_url": match.group(1),
                    "source": "Fallback"
                })
    except:
        pass
    
    return jsonify({
        "success": False,
        "error": "Video link nahi mila. API subscription required.",
        "solution": "RapidAPI par free subscribe karein: https://rapidapi.com/",
        "full_response": {"message": "Subscription required"}
    }), 404

@app.route('/')
def home():
    return "✅ Social Media Downloader Active! Use /download endpoint"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
