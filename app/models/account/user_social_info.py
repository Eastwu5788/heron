import datetime
from app import db
from app.models.base.base import BaseModel


class UserSocialInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_social_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    language = db.Column(db.String(20), default="")
    emotional_state = db.Column(db.String(20), default="")
    vocation_id = db.Column(db.Integer, default=0)
    vocation_name = db.Column(db.String(150), default="")
    company_name = db.Column(db.String(30), default="")
    school_id = db.Column(db.Integer, default=0)
    school_name = db.Column(db.String(150), default="")
    enrollment_time = db.Column(db.Integer, default=0)
    home_city_id = db.Column(db.Integer, default=0)
    home_city_name = db.Column(db.String(30), default="")
    work_region_id = db.Column(db.Integer, default=0)
    work_region_name = db.Column(db.String(30), default="")
    live_region_id = db.Column(db.Integer, default=0)
    live_region_name = db.Column(db.String(30), default="")
    about_me = db.Column(db.String(255), default="")

    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)