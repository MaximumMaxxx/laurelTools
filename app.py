import logging

from flask import render_template

from lib.globals import app, db
from blueprints.videoDownloader import videoDownloader
from blueprints.chat import chat

with app.app_context():
    db.create_all()

logging.basicConfig(
    filemode="a",
    level=logging.ERROR,
    filename="log.log",
)


@app.route("/")
def index():
    return render_template("index.html")


app.register_blueprint(videoDownloader, url_prefix="/videoDownloader/")
app.register_blueprint(chat, url_prefix="/chat/")

print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
