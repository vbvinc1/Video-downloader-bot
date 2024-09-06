from flask import Flask, request, jsonify
import yt_dlp
import m3u8
import ffmpeg
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    quality = request.json.get('quality', 'best')
    download_link = process_video(url, quality)
    return jsonify({'message': 'Video processed', 'download_link': download_link})

def process_video(url, quality):
    # Download video using yt-dlp
    ydl_opts = {
        'format': quality,
        'outtmpl': '/path/to/downloaded/video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)

    # Check if the video is an m3u8 stream
    if video_path.endswith('.m3u8'):
        m3u8_obj = m3u8.load(video_path)
        ts_files = [segment.uri for segment in m3u8_obj.segments]
        combined_video_path = '/path/to/downloaded/combined_video.mp4'
        ffmpeg.input('concat:' + '|'.join(ts_files)).output(combined_video_path).run()
        os.remove(video_path)
        return combined_video_path
    else:
        return video_path

if __name__ == '__main__':
    app.run(debug=True)
  
