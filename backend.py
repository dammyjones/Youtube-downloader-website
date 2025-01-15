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
def get_video_info():
    video_url = request.json.get('video_url', None)
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400

    logging.debug(f"Received video URL: {video_url}")
    try:
        # Ensure ydl_opts is properly defined before usage
        ydl_opts = {
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'client': 'web'  # Adjust client if necessary
                }
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            if not formats:
                raise ValueError("No formats found")

        logging.debug(f"Available formats: {formats}")
        return jsonify({'formats': formats})

    except Exception as e:
        # Log the exact error for debugging
        logging.error(f"Error fetching video info: {e}")
        return jsonify({'error': f"Failed to fetch formats: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
