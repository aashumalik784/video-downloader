from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp, os, uuid

app = Flask(__name__)
CORS(app)
DOWNLOAD_FOLDER = '/tmp/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "YT-DLP API is running! Backend ready hai ✅"

@app.route('/api/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL nahi diya'}), 400
    try:
        unique_id = str(uuid.uuid4())
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s',
            'noplaylist': True,
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return jsonify({
            'success': True,
            'download_url': f'/download/{os.path.basename(filename)}',
            'title': info.get('title', 'video')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404
