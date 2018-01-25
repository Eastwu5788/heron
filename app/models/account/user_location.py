import datetime
from app import db, cache
from app.models.base.base import BaseModel


class UserLocationModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_location"

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(32), default="")
    user_id = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Integer, default=0)
    longitude = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
