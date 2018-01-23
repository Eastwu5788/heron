import datetime
from app import db
from app.models.base.base import BaseModel
from app.models.social.share_meta import ShareMetaModel
from app.models.social.image import ImageModel
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
        result = query.all()
        if not result:
            result = []
        return result

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
        print(img_model_dict)

        # 逐条格式化
        for share_model in share_info_list:
            share_dic = share_model.to_dict()

            share_meta = share_meta_dict.get(share_model.share_id, None)
            share_dic["like_count"] = share_meta.like if share_meta else 0
            share_dic["comment_count"] = share_meta.comment if share_meta else 0
            share_dic["click"] = share_meta.click if share_meta else 0

            share_dic["like_list"] = []

            from app.models.account.user_info import UserInfoModel
            user_model = UserInfoModel.query_user_model_by_id(share_model.user_id)
            share_dic["user_info"] = UserInfoModel.format_user_info(user_model)

            share_dic["image"] = {}

            del share_dic["data"]

            result_list.append(share_dic)

        return result_list



