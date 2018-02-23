import datetime
from app.models.base.base import BaseModel
from app import db


class ShareMetaModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "share_meta"

    id = db.Column(db.Integer, primary_key=True)
    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    hit = db.Column(db.Integer, default=0)
    click = db.Column(db.Integer, default=0)
    like = db.Column(db.Integer, default=0)
    dislike = db.Column(db.Integer, default=0)
    comment = db.Column(db.Integer, default=0)
    report = db.Column(db.Integer, default=0)
    reward = db.Column(db.Integer, default=0)
    forward = db.Column(db.Integer, default=0)
    join = db.Column(db.Integer, default=0)
    subscribe = db.Column(db.Integer, default=0)
    reward_money = db.Column(db.Integer, default=0)
    sale = db.Column(db.Integer, default=0)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def update_share_meta_model(share_id=0, user_id=0, params=list(), meta_add=True):
        """
        更新share_meta的属性
        """
        if not share_id:
            return False

        share_meta = ShareMetaModel.query.filter_by(share_id=share_id).first()

        if not share_meta:
            share_meta = ShareMetaModel()
            share_meta.share_id = share_id

            if share_meta.user_id:
                share_meta.user_id = user_id

            db.session.add(share_meta)
            db.session.commit()

        for attr in params:
            if not attr:
                continue

            value = getattr(share_meta, attr)
            if not value:
                value = 0

            if meta_add:
                setattr(share_meta, attr, value+1)
            else:
                setattr(share_meta, attr, value-1)

        db.session.commit()

    @staticmethod
    def query_share_meta_model(share_id):
        return ShareMetaModel.query.filter_by(share_id=share_id).first()

    @staticmethod
    def query_share_meta_model_list(share_id_list=list(), auto_format=True):
        if not share_id_list:
            return []
        # 查询数据
        share_meta_model_list = ShareMetaModel.query.filter(ShareMetaModel.share_id.in_(share_id_list)).all()

        if not share_meta_model_list:
            share_meta_model_list = []
        # 不格式化，直接返回
        if not auto_format:
            return share_meta_model_list
        # 格式化
        return ShareMetaModel.format_share_meta_mode_list(share_meta_model_list)

    @staticmethod
    def format_share_meta_mode_list(share_meta_model_list=list()):
        """
        格式化ShareMeta模型，转换成标准字典
        :param share_meta_model_list: 原始模型字典
        :return: 格式化后的模型
        """
        result = []
        for share_meta in share_meta_model_list:
            item_dict = {
                "share_id": share_meta.share_id,
                "like_count": share_meta.like,
                "comment_count": share_meta.comment,
                "click": share_meta.click,
            }
            result.append(item_dict)
        return result
