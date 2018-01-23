import datetime
from app import db, cache
from app.models.base.base import BaseModel

user_info_cache_key_by_id = "UserInfoModel:QueryByID:"


class UserInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_info"

    __fillable__ = ["user_id", "identified", "identify_title", "nickname", "gender"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, default=0)
    role_data = db.Column(db.String(255), default="")
    identified = db.Column(db.Integer, default=0)
    identify_title = db.Column(db.String(20), default="")
    city_id = db.Column(db.Integer, default=0)
    city_name = db.Column(db.String(40), default="")
    nickname = db.Column(db.String(40), default="")
    gender = db.Column(db.Integer, default=0)
    avatar = db.Column(db.Integer, default=0)
    location_id = db.Column(db.Integer, default=0)
    cover = db.Column(db.Integer, default=0)
    cover_type = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_model_by_id(user_id, refresh=False):
        """
        根据用户模型查询用户信息模型
        :param user_id: 用户的id
        :param refresh: 是否刷新数据
        """
        cache_key = user_info_cache_key_by_id + str(user_id)
        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        user_info = UserInfoModel.query.filter_by(user_id=user_id, status=1).first()
        if user_info:
            cache.set(cache_key, user_info)
        return user_info

    @staticmethod
    def format_user_info(user, full=False):
        user_info_dict = user.to_dict(filter_params=not full)
        return user_info_dict

    @staticmethod
    def duplicate_nick_name(nickname, user_id):
        """
        大小写敏感的搜索用户昵称并排除自己
        :param nickname: 昵称
        :param user_id: 用户自己的id
        """
        result = UserInfoModel.query.filter_by(status=1).filter(user_id != user_id).filter(nickname=nickname).first()
        if result:
            return True
        return False

    @staticmethod
    def update_user_info(user_id, params=dict()):
        """
        更新用户信息
        :param user_id: 需要更新的用户ID
        :param params: 更新的参数
        """
        if not user_id or not params:
            return False

        UserInfoModel.query.filter_by(user_id=user_id, status=1).update(params)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
