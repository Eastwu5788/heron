from app import db, cache
from app.models.base.base import BaseModel
import datetime

user_access_token_cache_time = 60*60*24
user_access_token_cache_key = "UserAccessTokenModel:Token:"


class UserAccessTokenModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_access_token"

    __fillable__ = ["user_id", "device_type", "version", "bundle_id", "access_token", "salt", "udid"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    access_token = db.Column(db.String(32), default="")
    salt = db.Column(db.String(10), default="")

    device_token = db.Column(db.String(65), default="")
    device_type = db.Column(db.String(20), default="")
    udid = db.Column(db.String(40), default="")
    version = db.Column(db.String(30), default="")
    ip = db.Column(db.String(32), default="")
    user_agent = db.Column(db.String(255), default="")
    bundle_id = db.Column(db.String(255), default="")

    status = db.Column(db.Integer, default=0)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_useful_access_token(token, refresh=False):
        """
        查询可用的用户Token
        """
        cache_key = user_access_token_cache_key + token
        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = UserAccessTokenModel.query.filter_by(access_token=token, status=1).first()
        if result:
            cache.set(cache_key, result, user_access_token_cache_time)
        return result

    @staticmethod
    def bind_user_id(token, user_id):
        """
        绑定用户ID
        """
        UserAccessTokenModel.query.filter_by(access_token=token, status=1).update(dict(user_id=user_id))
        db.session.commit()

    @staticmethod
    def forbid_by_token(token):
        """
        禁用TOKEN
        """
        UserAccessTokenModel.query.filter_by(access_token=token, status=1).update(dict(status=0))
        db.session.commit()

