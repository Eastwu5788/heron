import datetime
from app.models.base.base import BaseModel
from app import db


class ImageModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "image"

    image_id = db.Column(db.Integer, primary_key=True)

    share_id = db.Column(db.Integer, default=0)
    album_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)

    type = db.Column(db.Integer, default=0)
    image_o = db.Column(db.String(100), default="")
    image_a = db.Column(db.String(100), default="")
    image_b = db.Column(db.String(100), default="")
    image_c = db.Column(db.String(100), default="")
    image_d = db.Column(db.String(100), default="")
    image_e = db.Column(db.String(100), default="")
    image_f = db.Column(db.String(100), default="")
    image_g = db.Column(db.String(100), default="")
    image_x = db.Column(db.String(100), default="")

    image_width = db.Column(db.Integer, default=0)
    image_height = db.Column(db.Integer, default=0)

    file_name = db.Column(db.String(32), default="")
    file_ext = db.Column(db.String(10), default="")
    mime_type = db.Column(db.String(20), default="")
    file_size = db.Column(db.Integer(), default=0)
    hash_key = db.Column(db.String(32), default="")

    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
