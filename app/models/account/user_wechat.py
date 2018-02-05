import datetime
from app import db

from app.models.base.base import BaseModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.account.user_info import UserInfoModel
from app.models.social.service_report import ServiceReportModel

from app.helper.utils import array_column, array_column_key


class UserWeChatModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_wechat"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    wechat = db.Column(db.String(21), default="")
    price = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_wechat_model(user_id):
        if not user_id:
            return None

        result = UserWeChatModel.query.filter_by(user_id=user_id).first()
        return result

    @staticmethod
    def format_user_wechat_data(order_meta_list, params, buyer_type="", seller_type=""):

        order_info_list = OrderInfoModel.query_order_info_model(array_column(order_meta_list, "order_id"))
        order_info_dict = array_column_key(order_info_list, "order_id")

        result = list()

        for order_meta in order_meta_list:
            item = dict()
            user_info_model = UserInfoModel.query_user_model_by_id(getattr(order_meta, seller_type, default=0))
            item["user_info"] = UserInfoModel.format_user_info(user_info_model) if user_info_model else dict()
            item["id"] = order_meta.id
            item["order_id"] = order_meta.order_id

            order_info = order_info_dict.get(order_meta.order_id)
            item["price"] = order_info.order_price / 100 if order_info else 0

            item["time"] = order_meta["created_time"]

            wechat_status = UserWeChatModel.format_wechat_status(order_meta, params["user_id"])
            item["wechat_complain_status"] = wechat_status.get("wechat_complain_status", 0)
            item["wechat_order_status"] = wechat_status.get("wechat_order_status", 0)

            if buyer_type == "seller_id":
                item["wechat"] = order_info.order_message if order_info else ""

            result.append(item)

        return result

    @staticmethod
    def format_wechat_status(order_meta, user_id):
        result = dict()
        status = order_meta.order_status
        if status == 2:
            if order_meta.buyer_id == user_id:
                result["wechat_complain_status"] = 1
                result["wechat_order_status"] = 1

            if order_meta.seller_id == user_id:
                result["wechat_complain_status"] = 0
                result["wechat_order_status"] = 1

        elif status == 3:
            if order_meta.buyer_id == user_id:
                result["wechat_complain_status"] = 0 if order_meta.complain_status > 0 else 1
                result["wechat_order_status"] = 1

            if order_meta.seller_id == user_id:
                result["wechat_complain_status"] = 1
                result["wechat_order_status"] = 0

        elif status == 5:
            result["wechat_complain_status"] = 2
            result["wechat_order_status"] = 1

        elif status == 6:
            service_report = ServiceReportModel.query_service_report(user_id, order_meta.seller_id, order_meta.order_id)
            result["wechat_complain_status"] = 0
            if service_report:
                result["wechat_complain_status"] = 1
            result["wechat_order_status"] = 0
        return result
