import datetime
from app.models.base.base import BaseModel
from app import db


class LikeModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "like"

    __fillable__ = ["like_id"]

    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_like_list(share_id, limit=20, auto_format=True):

        query = LikeModel.query.filter_by(share_id=share_id).order_by(LikeModel.like_id.desc())
        result = query.limit(limit).all()

        if not auto_format:
            return result

        return LikeModel.format_like_info(result)

    @staticmethod
    def query_like_model(user_id, share_id):

        return LikeModel.query.filter_by(user_id=user_id, share_id=share_id).first()

    @staticmethod
    def format_like_info(like_model_list=list()):

        result = []

        if not like_model_list:
            return result

        from app.models.account.user_info import UserInfoModel

        for model in like_model_list:
            user_info = UserInfoModel.query_user_model_by_id(model.user_id)
            user_info = UserInfoModel.format_user_info(user_info)

            item_dict = {
                "avatar": user_info.get("avatar", ""),
                "like_id": model.like_id,
            }

            result.append(item_dict)

        return result

