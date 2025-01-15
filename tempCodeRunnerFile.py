from flask import Flask, request, send_file, render_template
import os
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['video_url']
    format = request.form['format']
    quality = request.form['quality']
    try:
        # Configure yt-dlp
        ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'video[height>=1080]+bestaudio/best[ext=mp4]',  
        'quiet': True,
        'force_generic_extractor': True,
        

}


        # Create the 'downloads' directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)

        # Download the video
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', None)
            filename = ydl.prepare_filename(info_dict)

        # Serve the file for download
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
