import datetime
from sqlalchemy import or_, and_
from app import db
from app.models.base.base import BaseModel

from app.models.account.user_info import UserInfoModel
from app.models.social.share import ShareModel

from app.helper.utils import array_column, array_column_key


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
        """
        TODO：待完成
        """
        query = CommentModel.query.filter_by(share_id=share_id, status=1)

        if last_id:
            query = query.filter(CommentModel.comment_id < last_id)

        share_model = ShareModel.query_share_model(share_id)

        # 如果访问者不是发帖者，则只能显示自己的悄悄话和公开评论
        if share_model.user_id != login_user_id:
            query = query.filter(
                or_(
                    CommentModel.type == 0,
                    and_(CommentModel.type == 1, CommentModel.user_id == login_user_id),
                )
            )

        comment_list = query.filter(CommentModel.status == 1).order_by(CommentModel.comment_id.desc()).limit(per_page).all()
        if not comment_list:
            return []

        comment_dict_list = array_column_key(comment_list, "comment_id")

        # 获取所有的父评论id并去重
        layer_comment_id_list = list(set(array_column(comment_list, "layer_comment_id")))

        # 查找所有父评论的详情
        query = CommentModel.query.filter(CommentModel.comment_id.in_(layer_comment_id_list), CommentModel.status == 1)
        layer_comment_model_list = query.order_by(CommentModel.comment_id.desc()).all()

        for layer_comment_model in layer_comment_model_list:
            if layer_comment_model.type == 1 and login_user_id not in [layer_comment_model.user_id]:
                continue

            comment_model = comment_dict_list.get(layer_comment_model.comment_id, None)
            if not comment_model:
                continue

        result = list()
        for comment_model in comment_list:
            item = comment_model.to_dict()
            user_model = UserInfoModel.query_user_model_by_id(comment_model.user_id)
            item["user_info"] = UserInfoModel.format_user_info(user_model)
            if not item.get("layer_info", None):
                item["layer_info"] = []
            result.append(item)

        return result



