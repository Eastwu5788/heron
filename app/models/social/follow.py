import datetime
from app import db
from app.models.base.base import BaseModel


class FollowModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "follow"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    follow_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_follow_user_list(user_id):
        """
        查询某人关注的用户列表
        :param user_id: 用户id
        :return: 关注的用户列表
        """
        result = FollowModel.query.filter_by(user_id=user_id, status=1).all()
        if not result:
            result = []

        from app.helper.utils import array_column_index
        return array_column_index(result, 0)
