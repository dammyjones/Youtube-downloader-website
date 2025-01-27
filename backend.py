from flask import Flask, request, jsonify, render_template, send_file
from yt_dlp import YoutubeDL
import logging
import os

app = Flask(__name__)

# Enable debug-level logging
logging.basicConfig(level=logging.DEBUG)

# Define yt-dlp options (without format specification)
ydl_opts = {
    'noplaylist': True,
    'quiet': True,
    'outtmpl': 'downloads/%(title)s.%(ext)s',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_formats():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        if not video_url:
            return jsonify({'error': 'No video URL provided.'}), 400

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])

        return jsonify({
            'formats': [
                {
                    'format_id': fmt.get('format_id'),
                    'resolution': f"{fmt.get('width')}x{fmt.get('height')}" if fmt.get('width') and fmt.get('height') else 'Audio Only',
                    'ext': fmt.get('ext'),
                    'filesize': fmt.get('filesize'),
                    'acodec': fmt.get('acodec'),
                    'vcodec': fmt.get('vcodec'),
                    'url': fmt.get('url')
                } for fmt in formats if fmt.get('format_id') and fmt.get('url')
            ]
        })

    except Exception as e:
        logging.exception("Unexpected error")
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form.get('video_url')
        format_id = request.form.get('format_id')
        if not video_url or not format_id:
            return jsonify({'error': 'Video URL and format ID are required.'}), 400

        # Create a copy of the base options to avoid thread-safety issues
        download_opts = ydl_opts.copy()

        # First, extract info to check if the selected format is video-only
        with YoutubeDL(download_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            selected_format = next(
                (fmt for fmt in info_dict['formats'] if fmt['format_id'] == format_id),
                None
            )
            if not selected_format:
                return jsonify({'error': 'Invalid format ID.'}), 400

            # Check if the format is video-only (has no audio codec)
            if selected_format.get('acodec') == 'none':
                # Combine the selected video format with the best audio
                download_opts['format'] = f'{format_id}+bestaudio'
            else:
                # Use the selected format as-is (already includes audio)
                download_opts['format'] = format_id

        # Perform the download with the adjusted options
        with YoutubeDL(download_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logging.exception("Download error")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)