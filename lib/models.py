from .globals import db

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    uuid = db.Column(db.String, unique=True)
    remove = db.Column(db.Integer)
    url = db.Column(db.String)
