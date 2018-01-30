import datetime
from app import db, cache
from app.models.base.base import BaseModel

user_personal_info_cache_key = "UserPersonalInfoModel:QueryByID:"
user_personal_info_cache_time = 60*60*24


class UserPersonalInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_personal_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    age = db.Column(db.Integer, default=0)
    birthday = db.Column(db.DateTime, default=datetime.datetime(2000, 1, 1, 0, 0, 0))
    star_sign = db.Column(db.String(10), default="")
    weight = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)
    bust = db.Column(db.Integer, default=0)
    waist = db.Column(db.Integer, default=0)
    hips = db.Column(db.Integer, default=0)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_personal_info_by_user_id(user_id, refresh=False):
        cache_key = user_personal_info_cache_key + str(user_id)

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = UserPersonalInfoModel.query.filter_by(user_id=user_id).first()
        if result:
            cache.set(cache_key, result, user_personal_info_cache_time)

        return result

    @staticmethod
    def update_user_personal_info(user_id, params):
        """
        更新用户信息
        :param user_id: 需要更新的用户ID
        :param params: 更新的参数
        """
        if not user_id or not params:
            return False

        UserPersonalInfoModel.query.filter_by(user_id=user_id).update(params)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
