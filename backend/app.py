from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json

app = Flask(__name__)
CORS(app)

def extract_instagram_video(url):
    """Instagram video direct link extract karega"""
    try:
        # Instagram embed API use karte hain (free, no key)
        embed_url = url.replace("/reel/", "/p/").replace("/tv/", "/p/")
        
        # Pehle shortcode nikalte hain
        shortcode_match = re.search(r'instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if not shortcode_match:
            return None
        
        shortcode = shortcode_match.group(1)
        
        # Instagram graphql endpoint (public, no auth)
        graphql_url = f"https://www.instagram.com/p/{shortcode}/embed/"
        
        response = requests.get(graphql_url, timeout=10)
        if response.status_code == 200:
            # HTML se video URL extract
            video_match = re.search(r'video_url":"([^"]+)"', response.text)
            if video_match:
                video_url = video_match.group(1).replace('\\u0026', '&')
                return video_url
            
            # Alternative pattern
            video_match2 = re.search(r'<video[^>]+src="([^"]+)"', response.text)
            if video_match2:
                return video_match2.group(1)
        
        return None
    except Exception as e:
        print(f"Instagram error: {e}")
        return None

def extract_youtube_video(url):
    """YouTube video direct link extract (using yewtu/Invidious API)"""
    try:
        # Extract video ID
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&]|$)', url)
        if not video_id_match:
            return None
        
        video_id = video_id_match.group(1)
        
        # Free Invidious instance use karte hain
        invidious_instances = [
            f"https://yewtu.be/api/v1/videos/{video_id}",
            f"https://invidious.snopyta.org/api/v1/videos/{video_id}",
            f"https://inv.riverside.rocks/api/v1/videos/{video_id}"
        ]
        
        for instance in invidious_instances:
            try:
                response = requests.get(instance, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # Best quality video format dhundho
                    if 'formatStreams' in data:
                        for stream in data['formatStreams']:
                            if stream.get('type', '').startswith('video/mp4'):
                                return stream.get('url')
                    if 'adaptiveFormats' in data:
                        for stream in data['adaptiveFormats']:
                            if stream.get('type', '').startswith('video/mp4'):
                                return stream.get('url')
                break
            except:
                continue
        
        return None
    except Exception as e:
        print(f"YouTube error: {e}")
        return None

def extract_twitter_video(url):
    """Twitter/X video direct link extract"""
    try:
        # Fix Twitter/X URL
        url = url.replace("x.com", "twitter.com")
        
        # fxtwitter API (free, no key)
        api_url = url.replace("twitter.com", "fxtwitter.com")
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            # Extract video URL from response
            video_match = re.search(r'https?://[^\s"\']+\.(mp4|mov)[^\s"\']*', response.text)
            if video_match:
                return video_match.group(0)
        
        return None
    except Exception as e:
        print(f"Twitter error: {e}")
        return None

def extract_tiktok_video(url):
    """TikTok video direct link extract"""
    try:
        # TikTok video ID extract
        video_id_match = re.search(r'/video/(\d+)', url)
        if not video_id_match:
            return None
        
        video_id = video_id_match.group(1)
        
        # Free TikTok API (no auth)
        api_url = f"https://tikwm.com/api/?url={url}"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('play'):
                return data['data']['play']
            if data.get('data', {}).get('wmplay'):
                return data['data']['wmplay']
            if data.get('data', {}).get('hdplay'):
                return data['data']['hdplay']
        
        return None
    except Exception as e:
        print(f"TikTok error: {e}")
        return None

def extract_facebook_video(url):
    """Facebook video direct link extract"""
    try:
        # SnapSave API (free)
        api_url = "https://snapsave.app/fb"
        
        response = requests.post(api_url, data={"url": url}, timeout=10)
        if response.status_code == 200:
            video_match = re.search(r'(https?://[^\s"\']+\.mp4[^\s"\']*)', response.text)
            if video_match:
                return video_match.group(0)
        
        return None
    except Exception as e:
        print(f"Facebook error: {e}")
        return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    
    if not video_url:
        return jsonify({"error": "URL do bhai"}), 400
    
    # Platform detect karo
    video_link = None
    platform = "unknown"
    
    try:
        if 'instagram.com' in video_url.lower():
            platform = "Instagram"
            video_link = extract_instagram_video(video_url)
        
        elif 'youtube.com' in video_url.lower() or 'youtu.be' in video_url.lower():
            platform = "YouTube"
            video_link = extract_youtube_video(video_url)
        
        elif 'twitter.com' in video_url.lower() or 'x.com' in video_url.lower():
            platform = "Twitter/X"
            video_link = extract_twitter_video(video_url)
        
        elif 'tiktok.com' in video_url.lower():
            platform = "TikTok"
            video_link = extract_tiktok_video(video_url)
        
        elif 'facebook.com' in video_url.lower() or 'fb.com' in video_url.lower():
            platform = "Facebook"
            video_link = extract_facebook_video(video_url)
        
        else:
            return jsonify({
                "error": "Platform support nahi hai",
                "supported": ["Instagram", "YouTube", "Twitter", "TikTok", "Facebook"]
            }), 400
        
        if video_link:
            return jsonify({
                "success": True,
                "video_url": video_link,
                "platform": platform,
                "message": f"{platform} video ready! Click download button."
            })
        else:
            return jsonify({
                "success": False,
                "error": f"{platform} video link extract nahi ho paya. Try different link."
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ Social Media Downloader Active! Supports: Instagram, YouTube, Twitter, TikTok, Facebook"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
