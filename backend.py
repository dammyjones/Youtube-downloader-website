from flask import Flask, request, jsonify, render_template, send_file
from yt_dlp import YoutubeDL
import logging
import os
from functools import lru_cache

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Modified yt-dlp configuration with MP4 preferences
ydl_opts = {
    'noplaylist': True,
    'quiet': True,
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'concurrent_fragment_downloads': 16,
    'http_chunk_size': 10485760,
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '-x', '16',
        '-s', '16',
        '-k', '10M'
    ],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
    # Add postprocessor to prefer MP4 format
}

@lru_cache(maxsize=100)
def get_cached_info(url):
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_formats():
    try:
        video_url = request.json.get('video_url')
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        info_dict = get_cached_info(video_url)
        formats = info_dict.get('formats', [])

        return jsonify({
            'formats': [
                {
                    'format_id': fmt.get('format_id'),
                    'resolution': f"{fmt.get('width')}x{fmt.get('height')}" if fmt.get('width') else 'Audio',
                    'ext': fmt.get('ext'),
                    'filesize': fmt.get('filesize'),
                    'acodec': fmt.get('acodec'),
                    'vcodec': fmt.get('vcodec')
                } for fmt in formats if fmt.get('url')
            ]
        })

    except Exception as e:
        logging.error(f"Error getting formats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form['video_url']
        format_id = request.form['format_id']
        
        # Clone options to avoid thread conflicts
        download_opts = ydl_opts.copy()
        
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Find the selected format
            selected_format = next(
                (f for f in info['formats'] if f['format_id'] == format_id),
                None
            )
            
            if not selected_format:
                return jsonify({'error': 'Invalid format selected'}), 400

            # Handle formats without audio
            if selected_format.get('acodec') == 'none':
                # Prefer AAC audio for better MP4 compatibility
                download_opts['format'] = f'{format_id}+bestaudio[ext=m4a]/bestaudio'
                download_opts['merge_output_format'] = 'mp4'
            else:
                download_opts['format'] = format_id

            # Actual download
            ydl.download([video_url])
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        logging.error(f"Download failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)