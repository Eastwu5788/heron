from datetime import datetime
from app import db
from app.models.base.base import BaseModel


class AudioModel(db.Model, BaseModel):

    __bind_key__ = "a_social"
    __tablename__ = "audio"

    audio_id = db.Column(db.Integer, primary_key=True)
    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    audio_url = db.Column(db.String(100), default="")
    file_name = db.Column(db.String(32), default="")
    playing_time = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, default=0)
    file_ext = db.Column(db.String(10), default="")
    file_format = db.Column(db.String(20), default="")
    hash_key = db.Column(db.String(32), default="")
    bitrate_mode = db.Column(db.String(32), default="")
    mime_type = db.Column(db.String(20), default="")
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, params):
        if params:
            for key, value in params.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def format_audio_model(audio_model):
        result = dict()
        if not audio_model:
            return result

        from heron import app
        result = audio_model.format_model(["audio_id"])
        result["audio_url"] = app.config["AUDIO_HOST"] + audio_model.audio_url
        return result
