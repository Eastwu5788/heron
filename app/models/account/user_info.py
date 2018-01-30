import datetime
from app import db, cache
from app.models.base.base import BaseModel

from app.models.social.album import AlbumModel
from app.models.social.image import ImageModel

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
    def query_user_album(user_id):
        result = dict()
        album = AlbumModel.query_album_by_user_id(user_id)
        if not album:
            return result

        image_model_list = ImageModel.query_album_image_list(user_id, album.id)

        small_list = []
        big_list = []
        for image_model in image_model_list:
            small = big = dict()

            small["url"] = ImageModel.generate_image_url(image_model, 'b')
            small["width"] = 240
            small["height"] = 240
            small["image_id"] = image_model.image_id
            small_list.append(small)

            big["url"] = ImageModel.generate_image_url(image_model, 'f')
            big["width"] = 800
            big["height"] = 800
            big["image_id"] = image_model.image_id
            big_list.append(big)
        result["small"] = small_list
        result["big"] = big_list

        return result

    @staticmethod
    def format_user_info(user, full=False):
        user_info_dict = user.to_dict(filter_params=not full)

        if not user.avatar:
            user_info_dict["avatar"] = ""
            user_info_dict["big_avatar"] = ""
        else:
            from app.models.social.image import ImageModel
            img = ImageModel.query_image_by_id(user.avatar)
            user_info_dict["avatar"] = ImageModel.generate_image_url(img, size='b')
            user_info_dict["big_avatar"] = ImageModel.generate_image_url(img, size='f')

        return user_info_dict

    @staticmethod
    def duplicate_nick_name(nickname, user_id):
        """
        大小写敏感的搜索用户昵称并排除自己
        :param nickname: 昵称
        :param user_id: 用户自己的id
        """
        result = UserInfoModel.query.filter_by(nickname=nickname, status=1).filter(UserInfoModel.user_id != user_id).first()
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

    @staticmethod
    def calculate_ok_percent(user_id):
        from app.models.account.user_social_info import UserSocialInfoModel
        from app.models.account.user_personal_info import UserPersonalInfoModel

        user_info = UserInfoModel.query_user_model_by_id(user_id)
        social_info = UserSocialInfoModel.query_user_social_info(user_id)
        personal_info = UserPersonalInfoModel.query_personal_info_by_user_id(user_id)

        percent = 0

        # 检查头像是否完善
        if user_info.avatar:
            percent += 24

        if user_info.nickname:
            percent += 12

        if user_info.gender:
            percent += 8

        user_social_info = ["vocation_name", "school_name", "live_region_name", "language", "emotional_state"]
        for attr in user_social_info:
            if not social_info:
                continue

            value = getattr(social_info, attr, None)
            if not value:
                continue

            percent += 8

        user_personal_info = ["age", "star_sign"]
        for attr in user_personal_info:
            if not personal_info:
                continue
            value = getattr(personal_info, attr, None)
            if not value:
                continue

            percent += 8

        return percent if percent <= 100 else 100
