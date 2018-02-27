import datetime
import os
from app.models.base.base import BaseModel
from app import db, cache


class VideoModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "video"

    video_id = db.Column(db.Integer, primary_key=True)

    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    cover_id = db.Column(db.Integer, default=0)

    type = db.Column(db.Integer, default=0)
    video_url = db.Column(db.String(100), default="")
    video_width = db.Column(db.Integer, default=0)
    video_height = db.Column(db.Integer, default=0)

    screenshot_a = db.Column(db.String(100), default="")
    screenshot_b = db.Column(db.String(100), default="")
    screenshot_c = db.Column(db.String(100), default="")

    file_name = db.Column(db.String(32), default="")
    playing_time = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer(), default=0)
    file_ext = db.Column(db.String(10), default="")
    file_format = db.Column(db.String(20), default="")
    hash_key = db.Column(db.String(32), default="")
    bitrate_mode = db.Column(db.String(32), default="")
    mime_type = db.Column(db.String(20), default="")

    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, params=None):

        if params and isinstance(params, dict):
            for key, value in params.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            db.session.add(self)
            db.session.commit()

    @staticmethod
    def query_share_video_info(share_id):
        if not share_id:
            return None

        video = VideoModel.query.filter_by(share_id=share_id, status=1).first()
        return video

    @staticmethod
    def format_video_info(video_model):
        if not video_model or not isinstance(video_model, VideoModel):
            return dict()

        from app.models.social.image import ImageModel
        from heron import app

        cover_model = ImageModel.query_image_by_id(video_model.cover_id)

        result = video_model.format_model(attr_list=["video_width", "video_height"])
        result["video_url"] = app.config["VIDEO_HOST"] + video_model.video_url
        result["video_img"] = ImageModel.generate_image_url(cover_model, 'f')

        return result
