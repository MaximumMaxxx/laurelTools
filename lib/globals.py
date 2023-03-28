from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# I think this should be fine
app = Flask("__main__")
app.config.update(
    DOWNLOAD_DIR="downloads",
    SQLALCHEMY_DATABASE_URI="sqlite:///project.db"
)
db.init_app(app)
