import datetime
from app import db
from app.models.base.base import BaseModel


class UserFeedBackModel(db.Model, BaseModel):
    __bind_key__ = "a_core"
    __tablename__ = "user_feedback"
    __table_args__ = {'schema': 'a_core'}

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    content = db.Column(db.String(1000), default="")
    system = db.Column(db.String(100), default="")
    version = db.Column(db.String(50), default="")
    mobile_model = db.Column(db.String(50), default="")
    json_data = db.Column(db.String(200), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

