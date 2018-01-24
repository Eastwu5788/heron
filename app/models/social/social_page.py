import datetime
from app.models.base.base import BaseModel
from app.models.social.image import ImageModel
from app import db


class SocialPageModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "social_page"

    __fillable__ = ["cover_type", "cover"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    cover_type = db.Column(db.Integer, default=0)
    cover = db.Column(db.String(500), default="")
    feeling = db.Column(db.String(200), default="")
    top_share_id = db.Column(db.Integer, default=0)
    album_show = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_social_page_model(user_id, auto_format=True):
        social_page_model = SocialPageModel.query.filter_by(user_id=user_id, status=1).first()
        if not auto_format:
            return social_page_model

        if not social_page_model:
            social_page_model = SocialPageModel()

        result = social_page_model.to_dict(filter_params=True)

        if social_page_model.cover_type == 1:
            image_model = ImageModel.query_image_by_id(social_page_model.cover)
            result["cover"] = ImageModel.generate_image_url(image_model, 'f')
        elif social_page_model.cover_type == 2:
            pass

        return result
