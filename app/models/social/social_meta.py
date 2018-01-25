import datetime
from app import db
from app.models.base.base import BaseModel


class SocialMetaModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "social_meta"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    follower = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    share = db.Column(db.Integer, default=0)
    photo = db.Column(db.Integer, default=0)
    wechat_want = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, default=0)
    longitude = db.Column(db.Float, default=0)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def update_social_meta_model(user_id=0, params=list(), meta_add=True):
        """
        更新SocialMetaModel的参数
        :param user_id: 用户id
        :param params: 需要修改的参数列表
        :param meta_add: 增加参数还是减少参数
        """
        if not params:
            return

        social_meta = SocialMetaModel.query.filter_by(user_id=user_id).first()
        if not social_meta:
            social_meta = SocialMetaModel()
            social_meta.user_id = user_id
            db.session.add(social_meta)
            db.session.commit()

        for attr in params:
            if not attr:
                continue

            value = getattr(social_meta, attr)
            if not value:
                value = 0

            if meta_add:
                value += 1
            else:
                value -= 1

            setattr(social_meta, attr, value)

        db.session.commit()

    @staticmethod
    def query_social_meta_info(user_id):
        """
        查询用户社交信息，可以批量查询
        """
        if isinstance(user_id, list):
            result = SocialMetaModel.query.filter(SocialMetaModel.user_id.in_(user_id)).all()
            if not result:
                result = []
        else:
            result = SocialMetaModel.query.filter_by(user_id=user_id).first()

        return result
