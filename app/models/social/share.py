import datetime
from sqlalchemy import or_, and_
from app import db
from app.models.base.base import BaseModel
from app.models.social.share_meta import ShareMetaModel
from app.models.social.image import ImageModel
from app.models.social.like import LikeModel
from app.helper.utils import *

# 线上版本的类型列表
share_type_list = [1, 10, 11, 20, 30, 50, 51, 90]
# 审核版本的类型列表
share_type_test = [1, 10, 11, 20, 30, 50, 51]

# 所有人都可以看的动态状态
status_public = [1, 4]
# 只有自己才可以看到的动态状态
status_private = [1, 3, 4]


class ShareModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "share"

    share_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    type_id = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, default=0)
    title = db.Column(db.String(150), default="")
    content = db.Column(db.String(250), default="")
    image = db.Column(db.String(500), default="")
    data = db.Column(db.String(250), default="")
    price = db.Column(db.Integer, default=0)
    position = db.Column(db.String(100), default="")
    share_type = db.Column(db.Integer, default=0)
    sort = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, default=0)
    offer_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_share_info_list(share_id_list=list()):
        """
        查询所有share_id在[]中的动态信息
        """
        query = ShareModel.query.filter(ShareModel.share_id.in_(share_id_list), ShareModel.type_id.in_(share_type_list))
        query.filter(ShareModel.status.in_(status_private))
        result = query.order_by(ShareModel.share_id.desc()).all()
        if not result:
            result = []
        return result

    @staticmethod
    def query_share_model(share_id):
        return ShareModel.query.filter_by(share_id=share_id).first()

    @staticmethod
    def format_share_model(share_info_list=list(), account=0):
        """
        统一的格式化动态模型
        1. 动态格式化
        2. 图片格式化
        3. 评论格式化
        4. 点赞格式化
        """
        result_list = []
        if not share_info_list:
            return result_list

        share_id_list = array_column(share_info_list, "share_id")

        # 获取到share_meta模型(一次sql比多次sql要好)
        share_meta_list = ShareMetaModel.query_share_meta_model_list(share_id_list, auto_format=False)
        share_meta_dict = array_column_key(share_meta_list, "share_id")

        img_model_dict = ImageModel.query_share_image_list(share_id_list)

        like_status_list = ShareModel.query_share_check_list(account, share_id_list)

        # 逐条格式化
        for share_model in share_info_list:
            share_dic = share_model.to_dict()

            share_meta = share_meta_dict.get(share_model.share_id, None)
            share_dic["like_status"] = 1 if like_status_list.get(share_model.share_id, None) else 0
            share_dic["like_count"] = share_meta.like if share_meta else 0
            share_dic["comment_count"] = share_meta.comment if share_meta else 0
            share_dic["click"] = share_meta.click if share_meta else 0

            # 格式化用户信息
            from app.models.account.user_info import UserInfoModel
            user_model = UserInfoModel.query_user_model_by_id(share_model.user_id)
            share_dic["user_info"] = UserInfoModel.format_user_info(user_model)

            # 格式化图片信息
            img_model_list = img_model_dict.get(share_model.share_id, None)
            share_dic["image"] = {
                "big": ImageModel.format_image_model(img_model_list, size='f'),
                "small": ImageModel.format_image_model(img_model_list, size='c'),
            }

            share_dic["like_list"] = LikeModel.query_like_list(share_model.share_id, limit=5)

            # 删除无用数据
            del share_dic["data"]

            result_list.append(share_dic)

        return result_list

    @staticmethod
    def query_share_check_list(user_id, share_id_list):
        if not share_id_list or not user_id:
            return {}

        like_model_list = LikeModel.query.filter_by(user_id=user_id, status=1).filter(LikeModel.share_id.in_(share_id_list)).all()
        if not like_model_list:
            like_model_list = []

        return array_column_key(like_model_list, "share_id")

    @staticmethod
    def query_recent_share_photo(user_id, login_user, limit=3):
        """
        查询最近发布的三条动态的图片
        """
        query = ShareModel.query.filter_by(user_id=user_id, type_id=10)
        if user_id == login_user:
            query = query.filter(ShareModel.status.in_(status_private))
        else:
            query = query.filter(ShareModel.status.in_(status_public))

        result = query.order_by(ShareModel.share_id.desc()).limit(limit).all()

        if not result:
            return []

        share_ids_list = array_column(result, "share_id")

        query = ImageModel.query.filter_by(status=1).filter(ImageModel.share_id.in_(share_ids_list))
        image_list = query.order_by(ImageModel.image_id.desc()).limit(limit).all()
        if not image_list:
            image_list = []

        result = list()
        for image_model in image_list:
            url = ImageModel.generate_image_url(image_model, 'b')
            if url:
                result.append(url)

        return result

    @staticmethod
    def query_user_share_list(user_id_list=list(), login_user_id=0, limit=20, last_share_id=0, sort=0):
        """
        查询某些人的动态列表
        :param user_id_list: 需要查询的用户列表
        :param login_user_id: 当前登录用户
        :param limit: 分页数量
        :param last_share_id:最后一条动态id，用于分页
        :param sort: 排序
        :return: 查询结果
        """
        # 计算上自己的动态
        if login_user_id > 0:
            # 只查询自己的
            if not user_id_list:
                query = ShareModel.query.filter_by(user_id=login_user_id).filter(ShareModel.status.in_(status_private))
            # 同时查询自己和别人的
            else:
                query = ShareModel.query.filter(or_(
                    and_(ShareModel.user_id == login_user_id, ShareModel.status.in_(status_private)),
                    and_(ShareModel.user_id.in_(user_id_list), ShareModel.status.in_(status_public))
                ))
        # 只查询别人的动态
        else:
            if isinstance(user_id_list, list):
                query = ShareModel.query.filter(ShareModel.user_id.in_(user_id_list), ShareModel.parent_id == 0)
            else:
                query = ShareModel.query.filter_by(user_id=user_id_list, parent_id=0)

            query = query.filter(ShareModel.status.in_(status_public))

        query = query.filter(ShareModel.user_id > 0)
        if last_share_id > 0:
            query = query.filter(ShareModel.share_id < last_share_id)

        if sort > 0:
            query = query.order_by(ShareModel.sort.desc())
        result = query.order_by(ShareModel.share_id.desc()).limit(limit).all()
        if not result:
            return result

        return result
