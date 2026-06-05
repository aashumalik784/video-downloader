import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')
    
    # RapidAPI Endpoint
    url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    
    payload = {"url": video_url}
    headers = {
        "x-rapidapi-key": "
curl --request POST \
--url 
https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink
 \
--header 'Content-Type: application/json' \
--header 'x-rapidapi-host: auto-download-all-in-one.p.rapidapi.com' \
--header 'x-rapidapi-key: 45ceb2f534msh34e98d782a09e76p11792ejsnd963d248c5c1' \
--data '{"url":"
https://www.tiktok.com/@yeuphimzz/video/7237370304337628442
"}'", # Screenshot mein jo key hai wo yahan dalein
        "x-rapidapi-host": "auto-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
