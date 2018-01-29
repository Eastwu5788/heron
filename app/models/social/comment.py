import datetime
from app import db
from app.models.base.base import BaseModel

from app.models.account.user_info import UserInfoModel

from app.helper.utils import array_column


class CommentModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "comment"

    comment_id = db.Column(db.Integer, primary_key=True)
    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    reply_comment_id = db.Column(db.Integer, default=0)
    rate = db.Column(db.Integer, default=0)
    content = db.Column(db.String(250), default="")
    type = db.Column(db.Integer, default=0)
    layer_comment_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_comment_by_id(comment_id):
        return CommentModel.query.filter_by(comment_id=comment_id).first()

    @staticmethod
    def query_share_comment_list(share_id, login_user_id=0, last_id=0, per_page=20):

        query = CommentModel.query.filter_by(share_id=share_id, status=1)

        if last_id:
            query = query.filter(CommentModel.comment_id < last_id)

        comment_list = query.order_by(CommentModel.comment_id.desc()).limit(per_page).all()
        if not comment_list:
            comment_list = []

        result = []
        for comment_model in comment_list:
            comment_info = CommentModel.format_share_comment_model(comment_model, login_user_id)
            if comment_info:
                result.append(comment_info)
        return result

    @staticmethod
    def format_share_comment_model(comment_model, long_user_id=0):
        if not comment_model:
            return None

        comment_info = comment_model.to_dict()
        if comment_model.reply_comment_id:
            reply_comment_model = CommentModel.query_comment_by_id(comment_model.reply_comment_id)
            if reply_comment_model:
                reply_user_info = UserInfoModel.query_user_model_by_id(reply_comment_model.user_id)
                comment_info["reply_user_info"] = UserInfoModel.format_user_info(reply_user_info)

        comment_info["like"] = 1
        comment_info["like_count"] = 0

        user_info = UserInfoModel.query_user_model_by_id(comment_model.user_id)
        comment_info["user_info"] = UserInfoModel.format_user_info(user_info)

        return comment_info
