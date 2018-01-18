from app import db
from app.models.base.base import BaseModel
import datetime


class UserAccessTokenModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_access_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    access_token = db.Column(db.String(32), default="")
    salt = db.Column(db.String(10), default="")

    device_token = db.Column(db.String(65), default="")
    device_type = db.Column(db.String(20), default="")
    udid = db.Column(db.String(40), default="")
    version = db.Column(db.String(30), default="")
    ip = db.Column(db.String(32), default="")
    user_agent = db.Column(db.String(255), default="")
    bundle_id = db.Column(db.String(255), default="")

    status = db.Column(db.Integer, default=0)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
