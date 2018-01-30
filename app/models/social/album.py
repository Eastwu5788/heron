import datetime
from app import db
from app.models.base.base import BaseModel


class AlbumModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "album"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    album_name = db.Column(db.String(20), default="")
    album_cover = db.Column(db.String(100), default="")
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_album_by_user_id(user_id):
        """
        查询用户的相册
        :param user_id: 用户id
        :return: 相册模型
        """
        result = AlbumModel.query.filter_by(user_id=user_id, status=1).first()
        return result
