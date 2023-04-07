from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai
from dotenv import load_dotenv

import os

load_dotenv()

db = SQLAlchemy()
# I think this should be fine
app = Flask("__app__")
app.config.update(
    DOWNLOAD_DIR="downloads",
    SQLALCHEMY_DATABASE_URI="sqlite:///project.db"
)
db.init_app(app)
openai.api_key = os.getenv("OPENAI_API_KEY")

AUDIO = "wav"
AUDIO_VIDEO = "mp4"
