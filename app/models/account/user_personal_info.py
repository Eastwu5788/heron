import datetime
from app import db
from app.models.base.base import BaseModel


class UserPersonalInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_personal_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    age = db.Column(db.Integer, default=0)
    birthday = db.Column(db.DateTime, default=datetime.datetime(2000, 1, 1, 0, 0, 0))
    star_sign = db.Column(db.String(10), default="")
    weight = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)
    bust = db.Column(db.Integer, default=0)
    waist = db.Column(db.Integer, default=0)
    hips = db.Column(db.Integer, default=0)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)