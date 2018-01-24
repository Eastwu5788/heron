import datetime
from app import db
from app.models.base.base import BaseModel


class OpenLogModel(db.Model, BaseModel):
    __bind_key__ = "a_core"
    __tablename__ = "open_log"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, default=0)
    access_token = db.Column(db.String(32), default="")
    udid = db.Column(db.String(40), default="")
    device_type = db.Column(db.String(20), default="")
    version = db.Column(db.String(20), default="")
    type = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)