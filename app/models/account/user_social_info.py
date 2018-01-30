import datetime
from app import db, cache
from app.models.base.base import BaseModel

user_social_cache_key = "UserSocialInfoModel:QueryByID:"
user_social_cache_time = 60*60*24


class UserSocialInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_social_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    language = db.Column(db.String(20), default="")
    emotional_state = db.Column(db.String(20), default="")
    vocation_id = db.Column(db.Integer, default=0)
    vocation_name = db.Column(db.String(150), default="")
    company_name = db.Column(db.String(30), default="")
    school_id = db.Column(db.Integer, default=0)
    school_name = db.Column(db.String(150), default="")
    enrollment_time = db.Column(db.Integer, default=0)
    home_city_id = db.Column(db.Integer, default=0)
    home_city_name = db.Column(db.String(30), default="")
    work_region_id = db.Column(db.Integer, default=0)
    work_region_name = db.Column(db.String(30), default="")
    live_region_id = db.Column(db.Integer, default=0)
    live_region_name = db.Column(db.String(30), default="")
    about_me = db.Column(db.String(255), default="")

    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_social_info(user_id, refresh=False):
        cache_key = user_social_cache_key + str(user_id)

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = UserSocialInfoModel.query.filter_by(user_id=user_id).first()
        if result:
            cache.set(cache_key, result, user_social_cache_time)

        return result

    @staticmethod
    def update_user_social_info(user_id, params):
        """
        更新用户社交信息
        :param user_id: 用户id
        :param params: 更新参数
        :return: 返回值
        """

        if not user_id or not params:
            return False

        UserSocialInfoModel.query.filter_by(user_id=user_id).update(params)
        try:
            db.session.commit()
            return True
        except:
            return False
