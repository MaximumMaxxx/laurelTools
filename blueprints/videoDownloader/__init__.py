import time

import uuid
from yt_dlp import YoutubeDL
from flask import Blueprint, render_template, request, send_from_directory
from lib.globals import db, AUDIO_VIDEO, AUDIO, app
from lib.models import Download

videoDownloader = Blueprint("videoDownloader", __name__, template_folder="templates/")

@videoDownloader.route('/')
def index():  # put application's code here
    return render_template("dl/index.html", videoInfo=None, download=None)


@videoDownloader.post('/video')
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

    db.session.execute(db.insert(Download))

    vidDownload = Download(
        url=url,
        type=None,
        uuid=id,
        remove=int(time.time()) + 604800  # 7 days
    )
    db.session.add(vidDownload)
    db.session.commit()
    return render_template("dl/index.html", videoInfo=videoInfo, download=None)


@videoDownloader.post('/waiting/<dlid>')
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

    return render_template("dl/loading.html", dlid=dlid)


@videoDownloader.route("/download/<dlid>")
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

        return render_template("dl/index.html", download=f"{ogdl.uuid}.{ogdl.type}", videoInfo=None)


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
    return render_template("dl/index.html", download=f"{dlid}.{dlidVideo.type}", videoInfo=None)


@app.get(f"/{app.config['DOWNLOAD_DIR']}/<path:path>")
def send_file(path):
    return send_from_directory(
        directory=f"./{app.config['DOWNLOAD_DIR']}/", path=path
    )
