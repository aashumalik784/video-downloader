from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json

app = Flask(__name__)
CORS(app)

def extract_instagram_video(url):
    """Instagram video extract - Working method"""
    try:
        # Method 1: SnapInsta API (Free, no key)
        snapinsta_url = "https://snapinsta.app/api/ajaxSearch"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://snapinsta.app",
            "Referer": "https://snapinsta.app/"
        }
        
        data = {"q": url, "t": "media", "lang": "en"}
        
        response = requests.post(snapinsta_url, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract video URL from response
            if 'data' in result:
                html_content = result['data']
                
                # Find video URLs
                video_patterns = [
                    r'<video[^>]+src="([^"]+)"',
                    r'"url":"([^"]+\.mp4[^"]*)"',
                    r'href="([^"]+\.mp4[^"]+)"'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        for match in matches:
                            if '.mp4' in match:
                                return match.replace('\\/', '/')
            
            # Method 2: Alternative direct URL extraction
            download_url_match = re.search(r'<a[^>]+href="([^"]+\.mp4[^"]+)"[^>]*>Download', response.text)
            if download_url_match:
                return download_url_match.group(1)
        
        # Method 3: Instagram embed method (fallback)
        shortcode_match = re.search(r'instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if shortcode_match:
            shortcode = shortcode_match.group(1)
            embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
            
            embed_response = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if embed_response.status_code == 200:
                video_match = re.search(r'<video[^>]+src="([^"]+\.mp4[^"]+)"', embed_response.text)
                if video_match:
                    return video_match.group(1)
        
        return None
        
    except Exception as e:
        print(f"Instagram error: {e}")
        return None

def extract_youtube_video(url):
    """YouTube video extract"""
    try:
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&]|$)', url)
        if not video_id_match:
            return None
        
        video_id = video_id_match.group(1)
        
        # Using yewtu.be (Invidious instance)
        api_url = f"https://yewtu.be/api/v1/videos/{video_id}"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Get best quality video
            if 'adaptiveFormats' in data:
                for stream in data['adaptiveFormats']:
                    if stream.get('type', '').startswith('video/mp4') and stream.get('height', 0) >= 720:
                        return stream.get('url')
            
            if 'formatStreams' in data:
                for stream in data['formatStreams']:
                    if stream.get('type', '').startswith('video/mp4'):
                        return stream.get('url')
        
        return None
    except Exception as e:
        print(f"YouTube error: {e}")
        return None

def extract_twitter_video(url):
    """Twitter/X video extract"""
    try:
        url = url.replace("x.com", "twitter.com")
        
        # Using fxtwitter.com
        api_url = url.replace("twitter.com", "fxtwitter.com")
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            # Find MP4 URL
            video_patterns = [
                r'https?://video\.twimg\.com/[^\s"\']+\.mp4[^\s"\']*',
                r'https?://[^\s"\']+\.mp4[^\s"\']*'
            ]
            
            for pattern in video_patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(0)
        
        return None
    except Exception as e:
        print(f"Twitter error: {e}")
        return None

def extract_tiktok_video(url):
    """TikTok video extract"""
    try:
        # Using tikwm.com API
        api_url = f"https://tikwm.com/api/?url={url}"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('data'):
                # Priority: HD > no watermark > regular
                if data['data'].get('hdplay'):
                    return data['data']['hdplay']
                if data['data'].get('play'):
                    return data['data']['play']
                if data['data'].get('wmplay'):
                    return data['data']['wmplay']
        
        return None
    except Exception as e:
        print(f"TikTok error: {e}")
        return None

def extract_facebook_video(url):
    """Facebook video extract"""
    try:
        # Using snapsave.io
        api_url = "https://snapsave.io/fb"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"url": url}
        
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            # Extract video URL
            patterns = [
                r'<a[^>]+href="([^"]+\.mp4[^"]+)"[^>]*>Download',
                r'"hd_src":"([^"]+)"',
                r'"sd_src":"([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    url = match.group(1).replace('\\/', '/')
                    return url
        
        return None
    except Exception as e:
        print(f"Facebook error: {e}")
        return None

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    
    if not video_url:
        return jsonify({"error": "URL do bhai"}), 400
    
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
                "success": False,
                "error": "Platform support nahi hai",
                "supported": ["Instagram", "YouTube", "Twitter", "TikTok", "Facebook"]
            }), 400
        
        if video_link:
            return jsonify({
                "success": True,
                "video_url": video_link,
                "platform": platform,
                "message": f"✅ {platform} video ready! Click download button."
            })
        else:
            return jsonify({
                "success": False,
                "error": f"❌ {platform} video link extract nahi ho paya. Try different link or video.",
                "tip": "Instagram public account ki video daalo, private video kaam nahi karegi"
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "message": "Social Media Downloader API",
        "supported_platforms": ["Instagram", "YouTube", "Twitter", "TikTok", "Facebook"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
