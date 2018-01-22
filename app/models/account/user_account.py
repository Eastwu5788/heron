import datetime
from app import db, cache
from app.models.base.base import BaseModel


class UserAccountModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_account"

    __fillable__ = ["id", "mobile", "country", "password"]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), default="")

    mobile = db.Column(db.String(15), default="")
    country = db.Column(db.String(10), default="")
    email = db.Column(db.String(50), default="")
    password = db.Column(db.String(64), default="")
    user_salt = db.Column(db.String(10), default="")
    must_change_password = db.Column(db.Integer, default=0)
    banned = db.Column(db.Integer, default=0)
    suspended = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    openid = db.Column(db.String(40), default="")

    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_account_by_mobile(mobile="", country=86, refresh=False):
        cache_key = "Models:UserAccountModel:QueryByMobile:" + str(country) + mobile
        cache_time = 60*60*24

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = UserAccountModel.query.filter_by(mobile=mobile, country=country, status=1).first()
        if result:
            cache.set(cache_key, result, cache_time)
        return result

    @staticmethod
    def query_account_by_user_id(user_id):
        """
        根据user_id查找用户账户
        主键查找，不需要缓存
        """
        return UserAccountModel.query.filter_by(id=user_id, status=1).first()

    @staticmethod
    def update_account_password(user_id, mobile, country, password):
        """
        更新用户账户的密码
        """
        UserAccountModel.query.filter_by(id=user_id).update(dict(password=password))
        UserAccountModel.query_account_by_mobile(mobile, country, refresh=True)
        db.session.commit()
