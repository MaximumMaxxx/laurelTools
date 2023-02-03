import time

from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import logging
import uuid

db = SQLAlchemy()
app = Flask(__name__)
app.config.update(
    DOWNLOAD_DIR="downloads",
    SQLALCHEMY_DATABASE_URI="sqlite:///project.db"
)
db.init_app(app)


class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    uuid = db.Column(db.String, unique=True)
    remove = db.Column(db.Integer)
    url = db.Column(db.String)


with app.app_context():
    db.create_all()

logging.basicConfig(
    filemode="a",
    level=logging.ERROR,
    filename="log.log",
)

AUDIO = "wav"
AUDIO_VIDEO = "mp4"


# Simple state management for downloads

@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html", videoInfo=None, download=None)


@app.post('/video')
def video():
    url = request.form["url"]
    # Get video info
    id = uuid.uuid4().hex
    try:
        with YoutubeDL() as infoExtractor:
            info = infoExtractor.extract_info(
                url, download=False
            )
        videoInfo = {"thumbnail": info['thumbnail'], "dlid": id}
    except Exception:
        # URL wasn't valid
        videoInfo = None
    print("Made it past downloading!")

    db.session.execute(db.insert(Download))

    vidDownload = Download(
        url=url,
        type=None,
        uuid=id,
        remove=int(time.time()) + 604800  # 7 days
    )
    db.session.add(vidDownload)
    db.session.commit()
    return render_template("index.html", videoInfo=videoInfo, download=None)


@app.post('/waiting/<dlid>')
def waiting(dlid):
    dltype = request.form.get("Type")

    db.session.execute(
        db.update(Download)
        .where(Download.uuid == dlid)
        .values(
            type=dltype
        )
    )
    db.session.commit()

    return render_template("loading.html", dlid=dlid)


@app.route("/download/<dlid>")
def download(dlid):
    dlidVideo = db.session.execute(db.select(Download).where(Download.uuid == dlid)).scalar()

    otherDownload = db.session.execute(
        db.select(Download)
        .where(Download.url == dlidVideo.url)
        .where(Download.type == dlidVideo.type)
    ).scalars().all()

    if len(otherDownload) >= 2:
        # We've already downloaded the file
        # Saves time and money for me and the end user

        # Select the duplicate we just made, so we can remove it
        dl = db.session.execute(
            db.select(Download)
            .where(Download.uuid == dlid)
        ).scalar()

        db.session.delete(dl)
        db.session.commit()

        ogdl = db.session.execute(
            db.select(Download)
            .where(Download.uuid != dlid)
            .where(Download.type == dlidVideo.type)
            .where(Download.url == dlidVideo.url)
        ).scalar()

        return render_template("index.html", download=f"{ogdl.uuid}.{ogdl.type}", videoInfo=None)


    dllocation = f"./{app.config['DOWNLOAD_DIR']}/{dlid}"
    opts = {}

    if dlidVideo.type == AUDIO:
        opts = {
            "outtmpl": dllocation,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
    else:
        opts = {
            "outtmpl": dllocation,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

    with YoutubeDL(opts) as downloader:
        downloader.download([dlidVideo.url])
    return render_template("index.html", download=f"{dlid}.{dlidVideo.type}", videoInfo=None)


@app.get(f"/{app.config['DOWNLOAD_DIR']}/<path:path>")
def send_file(path):
    return send_from_directory(
        directory=f"./{app.config['DOWNLOAD_DIR']}/", path=path
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
