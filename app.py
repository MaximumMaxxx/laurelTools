from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, send_from_directory
import logging
import uuid
from collections import namedtuple

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# A little global config
Tvideo = namedtuple("download", "format videoUrl extension")
AUDIO = "A"
AUDIO_VIDEO = "B"

# Simple state management for downloads
downloads: "dict[str, video]" = {}

@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html",videoInfo=None, download=None)


@app.post('/video')
def video():
    url = request.form["url"]
    # Get video info
    id = uuid.uuid4().hex
    try:
        with YoutubeDL() as downloader:
            info = downloader.extract_info(
                url, download=False
            )
        videoInfo = {"thumbnail": info['thumbnail'], "dlid": id}
    except Exception:
        videoInfo = None
    vid = Tvideo
    vid.videoUrl = url
    downloads[id] = vid
    return render_template("index.html", videoInfo=videoInfo, download=None)

@app.post('/waiting/<dlid>')
def waiting(dlid):
    downloads[dlid].type = request.form.get("Type")
    return render_template("loading.html", dlid=dlid)

@app.route("/download/<dlid>")
def download(dlid):
    video = downloads[dlid]
    print(f"Downloading the file {video}")

    dllocation = f"downloads/{dlid}"
    opts = {}

    if video.type == AUDIO:
        opts = {
        "outtmpl": dllocation,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        video.extension = ".wav"
    else:
        opts = {
            "outtmpl": dllocation,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        video.extension = ".mp4"


    with YoutubeDL(opts) as downloader:
        downloader.download([video.videoUrl])
    downloads.pop(dlid)
    return render_template("index.html", download=dlid+video.extension, videoInfo=None)

@app.get("/downloads/<path:path>")
def send_file(path):
    return send_from_directory(
        directory="./downloads/", path=path
    )

if __name__ == '__main__':
    app.run(debug=True)
