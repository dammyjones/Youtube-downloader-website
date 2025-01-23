from flask import Flask, request, jsonify, render_template
from yt_dlp import YoutubeDL
import logging

app = Flask(__name__)

# Define the root route
@app.route('/')
def index():
    return render_template('index.html')  # Ensure 'index.html' exists in the 'templates' folder

# Enable debug-level logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/get_video_info', methods=['POST'])
@app.route('/get_video_info', methods=['POST'])
def get_video_formats():
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            if not formats:
                return jsonify({'error': 'No downloadable formats available.'}), 404
    except Exception as e:
        if "Failed to extract any player response" in str(e):
            return jsonify({'error': 'YouTube extractor failed. Please ensure yt-dlp is updated.'}), 500
        logging.exception("Unexpected error")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
