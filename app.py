from flask import Flask, request, send_file, jsonify
from pytube import YouTube
import instaloader
import os
import yt_dlp

app = Flask(__name__)

# Download YouTube video
def download_youtube(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    filename = stream.default_filename
    stream.download(output_path="downloads")
    return filename

# Download Instagram video/reel
def download_instagram(url):
    loader = instaloader.Instaloader()
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    filename = f"instagram_{post.owner_username}_{post.date_utc}.mp4"
    loader.download_post(post, target=f"downloads/{filename}")
    return filename

# Download Twitter video
def download_twitter(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if 'youtube.com' in url or 'youtu.be' in url:
        filename = download_youtube(url)
    elif 'instagram.com' in url:
        filename = download_instagram(url)
    elif 'twitter.com' in url or 'x.com' in url:
        filename = download_twitter(url)
    else:
        return jsonify({"error": "Unsupported URL"}), 400

    return send_file(os.path.join("downloads", filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    app.run(debug=True)
