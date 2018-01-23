import datetime
from app.models.base.base import BaseModel
from app import db


class ShareRecommendModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "share_recommend"

    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    share_type = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, share_id, user_id, position, status):
        """
        构造方法
        :param share_id: 动态id
        :param user_id: 用户id
        :param position: 位置
        :param status: 状态
        """
        self.share_id = share_id
        self.user_id = user_id
        self.position = position
        self.status = status

        db.session.add(self)
        db.session.commit()
