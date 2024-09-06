from flask import Flask, request, jsonify, send_file
import yt_dlp
import m3u8
import ffmpeg
import os
from pytube import YouTube
from io import BytesIO

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    quality = request.json.get('quality', 'best')
    try:
        download_link = process_video_yt_dlp(url, quality)
    except Exception as e:
        print(f"yt-dlp failed: {e}")
        try:
            download_link = process_video_pytube(url, quality)
        except Exception as e:
            print(f"pytube failed: {e}")
            return jsonify({'message': 'Failed to download video', 'error': str(e)}), 500
    return jsonify({'message': 'Video processed', 'download_link': download_link})

def process_video_yt_dlp(url, quality):
    ydl_opts = {
        'format': quality,
        'outtmpl': '/path/to/downloaded/video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)

    if video_path.endswith('.m3u8'):
        m3u8_obj = m3u8.load(video_path)
        ts_files = [segment.uri for segment in m3u8_obj.segments]
        combined_video_path = '/path/to/downloaded/combined_video.mp4'
        ffmpeg.input('concat:' + '|'.join(ts_files)).output(combined_video_path).run()
        os.remove(video_path)
        return combined_video_path
    else:
        return video_path

def process_video_pytube(url, quality):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4', res=quality).first()
    if not stream:
        stream = yt.streams.get_highest_resolution()
    video_path = stream.download(output_path='/path/to/downloaded/')
    return video_path

@app.route('/stream/<path:filename>', methods=['GET'])
def stream_video(filename):
    return send_file(filename, as_attachment=False)

@app.route('/download/<path:filename>', methods=['GET'])
def download_video_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
  
