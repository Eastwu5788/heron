import datetime
from app import db
from app.models.base.base import BaseModel


class AhaAccountModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "aha_account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    aha_id = db.Column(db.String(20), default="")
    changeable_aha = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)