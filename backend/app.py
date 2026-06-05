from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import re

app = Flask(__name__)
CORS(app)

def get_video_direct_url(video_url):
    """yt-dlp se direct video URL extract karega - BINA DOWNLOAD KARE"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'format': 'best[ext=mp4]/best',  # Best quality MP4
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Direct video URL dhundho
            if 'url' in info:
                return info['url']
            
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry and 'url' in entry:
                        return entry['url']
            
            if 'formats' in info:
                # Sabse high quality wala format lelo
                for f in info['formats']:
                    if f.get('ext') == 'mp4' and f.get('acodec') != 'none':
                        return f['url']
            
            return None
            
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    
    if not video_url:
        return jsonify({"error": "URL do bhai"}), 400
    
    # Platform validation
    supported = ['instagram.com', 'youtube.com', 'youtu.be', 'tiktok.com', 
                 'twitter.com', 'x.com', 'facebook.com', 'fb.com']
    
    if not any(platform in video_url.lower() for platform in supported):
        return jsonify({"error": "Yeh platform support nahi hai", "supported": supported}), 400
    
    try:
        video_direct_url = get_video_direct_url(video_url)
        
        if video_direct_url:
            return jsonify({
                "success": True,
                "video_url": video_direct_url,
                "message": "Video ready! Click download button."
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Video link extract nahi ho paya. URL check kar le."
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ Social Media Downloader Active! Free yt-dlp version"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
