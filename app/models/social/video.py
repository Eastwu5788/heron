import datetime
import os
from app.models.base.base import BaseModel
from app.models.social.image import ImageModel
from app.models.social.video_meta import VideoMetaModel
from app.models.commerce.order_video import OrderVideoModel
from app.helper.utils import array_column, array_column_key
from app import db, cache


class VideoModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "video"

    video_id = db.Column(db.Integer, primary_key=True)

    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    cover_id = db.Column(db.Integer, default=0)

    type = db.Column(db.Integer, default=0)
    video_url = db.Column(db.String(100), default="")
    video_width = db.Column(db.Integer, default=0)
    video_height = db.Column(db.Integer, default=0)

    screenshot_a = db.Column(db.String(100), default="")
    screenshot_b = db.Column(db.String(100), default="")
    screenshot_c = db.Column(db.String(100), default="")

    file_name = db.Column(db.String(32), default="")
    playing_time = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer(), default=0)
    file_ext = db.Column(db.String(10), default="")
    file_format = db.Column(db.String(20), default="")
    hash_key = db.Column(db.String(32), default="")
    bitrate_mode = db.Column(db.String(32), default="")
    mime_type = db.Column(db.String(20), default="")

    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, params=None):

        if params and isinstance(params, dict):
            for key, value in params.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            db.session.add(self)
            db.session.commit()

    @staticmethod
    def query_share_video_info(share_id):
        if not share_id:
            return None

        video = VideoModel.query.filter_by(share_id=share_id, status=1).first()
        return video

    @staticmethod
    def query_private_video(user_id, login_user_id, last_id=0):
        """
        顺序查询某人的私密视频列表
        :param user_id: 用户id
        :param login_user_id: 登录用户id
        :param last_id: 最后一个视频id
        """
        if not user_id or not login_user_id:
            return []

        query = VideoModel.query.filter_by(user_id=user_id, type=31, status=1)
        if last_id:
            query = query.filter(VideoModel.video_id < last_id)
        result = query.order_by(VideoModel.video_id.desc()).limit(15).all()
        if not result:
            return []

        return VideoModel.format_private_video_list(result, user_id, login_user_id)

    @staticmethod
    def query_random_private_video(user_id, login_user_id, last_id, offset=0, limit=15):
        """
        随机查询某人的私密视频
        :param user_id: 用户id
        :param login_user_id: 登录用户id
        :param last_id: 最后一条数据id
        :param offset: 初始偏移
        :param limit: 分页数量
        """
        invalid_video_list = OrderVideoModel.query_invalid_order_video_list(user_id, login_user_id)
        invalid_video_id_list = array_column(invalid_video_list, "video_id")

        result_1 = VideoModel.query_random_video_list(user_id, last_id, offset, limit, invalid_video_id_list)
        if len(result_1) == limit:
            return VideoModel.format_private_video_list(result_1, user_id, login_user_id)

        if last_id > offset or last_id == 0:
            last_id = 0.5
            limit = limit - len(result_1)
        else:
            return VideoModel.format_private_video_list(result_1, user_id, login_user_id)

        result_2 = VideoModel.query_random_video_list(user_id, last_id, offset, limit, invalid_video_id_list)
        result_1 += result_2

        return VideoModel.format_private_video_list(result_1, user_id, login_user_id)

    @staticmethod
    def query_random_video_list(user_id, last_id, offset, limit, invalid_video_id_list=list()):
        query = VideoModel.query.filter_by(user_id=user_id, type=31, status=1)

        if offset > 0:
            if last_id == 0:
                query = query.filter(VideoModel.video_id > offset)
            elif last_id > offset:
                query = query.filter(VideoModel.video_id > last_id)
            else:
                query = query.filter(VideoModel.video_id > last_id, VideoModel.video_id <= offset)

        if invalid_video_id_list:
            query = query.filter(VideoModel.video_id.notin_(invalid_video_id_list))

        result = query.order_by(VideoModel.video_id.asc()).limit(limit).all()
        if not result:
            result = []

        return result

    @staticmethod
    def format_video_info(video_model):
        if not video_model or not isinstance(video_model, VideoModel):
            return dict()

        from app.models.social.image import ImageModel
        from heron import app

        cover_model = ImageModel.query_image_by_id(video_model.cover_id)

        result = video_model.format_model(attr_list=["video_width", "video_height"])
        result["video_url"] = app.config["VIDEO_HOST"] + video_model.video_url
        result["video_img"] = ImageModel.generate_image_url(cover_model, 'f')

        return result

    @staticmethod
    def format_private_video_list(video_list, user_id, login_user_id):
        """
        格式化私密视频列表
        :param video_list: 原始私密视频模型
        :param user_id: 私密视频所属用户id
        :param login_user_id: 登录用户id
        :return: 格式化后的私密视频列表
        """
        image_model_list = ImageModel.query_image_by_image_id_list(array_column(video_list, "cover_id"))
        image_model_dict = array_column_key(image_model_list, "image_id")

        video_id_list = array_column(video_list, "video_id")
        video_meta_list = VideoMetaModel.query_video_meta_list(video_id_list)
        video_meta_dict = array_column_key(video_meta_list, "video_id")

        video_pay_dict = dict()
        if user_id != login_user_id:
            video_pay_list = OrderVideoModel.query_order_video_list(login_user_id, video_id_list)
            video_pay_dict = array_column_key(video_pay_list, "video_id")

        result = []

        for video_model in video_list:

            image_model = image_model_dict.get(video_model.cover_id, None)
            video_meta_model = video_meta_dict.get(video_model.video_id, None)

            if user_id == login_user_id:
                video_pay = 1
            else:
                order_video = video_pay_dict.get(video_model.video_id, None)
                video_pay = 1 if order_video else 0

            item = VideoModel.format_private_video_model(video_model, image_model, video_meta_model, video_pay)
            if item:
                result.append(item)

        return result

    @staticmethod
    def format_private_video_model(video_model=None, image_model=None, video_meta_model=None, pay=0):
        if not video_model:
            return dict()

        if not image_model:
            image_model = ImageModel.query_image_by_id(video_model.cover_id)
            if not image_model:
                return dict()

        if not video_meta_model:
            video_meta_model = VideoMetaModel.query_video_meta(video_model.video_id)
            if not video_meta_model:
                return dict()
        result = dict()

        result["pay"] = pay
        result["price"] = video_meta_model.price / 100

        video_dict = VideoModel.format_video_info(video_model)
        video_dict["video_id"] = video_model.video_id

        if not pay:
            video_dict["video_img"] = ImageModel.generate_image_url(image_model, 'x')
            video_dict["video_url"] = ""

        result["video"] = video_dict

        return result
