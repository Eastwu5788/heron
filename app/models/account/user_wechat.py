import datetime, time
from app import db

from app.models.base.base import BaseModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.commerce.order_meta import OrderMetaModel
from app.models.account.user_info import UserInfoModel
from app.models.social.service_report import ServiceReportModel
from app.models.commerce.order_notice import OrderNoticeModel

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
    def full_wechat_info(seller_id, buyer_id):
        result = {
            "wechat_status": 0,
            "wechat_price": 0,
            "wechat": "",
            "wechat_buy_status": 0,
            "wechat_sell_num": 0,
            "wechat_added": 0,
            "wechat_want_buy": 0,
            "wechat_want_buy_status": 0,
        }

        # 卖家是否设置了微信号
        seller_wechat = UserWeChatModel.query_user_wechat_model(seller_id)
        if seller_wechat:
            result["wechat_status"] = seller_wechat.status
            result["wechat_price"] = seller_wechat.price / 100

            # 买家是否买过对方的微信号
            me_buy_other = UserWeChatModel.check_buy_wechat(seller_id, buyer_id)
            if me_buy_other["wechat_buy_status"] == 1:
                # 买家是否提醒过卖家发货
                order_notice = OrderNoticeModel.query_order_notice(me_buy_other["order_id"], buyer_id)
                order_time = time.mktime(me_buy_other["created_time"])

                result["wechat_buy_status"] = 1
                result["wechat_added"] = me_buy_other["wechat_added"]
                result["wechat_remind_status"] = 1 if order_notice else 0
                result["wechat_order_end"] = 1 if time.time() - order_time > 43200 else 0
        else:
            result["wechat_status"] = 2

        # 对方购买过我的微信号
        other_by_me = UserWeChatModel.check_buy_wechat(buyer_id, seller_id)
        if other_by_me["wechat_buy_status"] == 1:
            order_info = OrderInfoModel.query_order_info_model(other_by_me["order_id"])
            order_time = time.mktime(other_by_me["created_time"])

            result["wechat_buy_status"] = 2
            result["wechat"] = order_info["order_message"]
            result["wechat_added"] = other_by_me["wechat_added"]
            result["wechat_order_end"] = 1 if time.time() - order_time > 43200 else 0

        return result

    @staticmethod
    def check_buy_wechat(user_id, buyer_id):
        query = OrderMetaModel.query.filter_by(seller_id=user_id, product_type=80, pay_status=1)
        sell_num = query.count()
        order_meta = query.filter_by(buyer_id=buyer_id).first()

        result = {
            "wechat_buy_status": 1 if order_meta else 0,
            "wechat_sell_num": sell_num,
            "wechat_added": 0,
            "order_id": order_meta.order_id if order_meta else 0,
            "created_time": order_meta.created_time if order_meta else 0
        }

        if order_meta and order_meta.ship_status == 3:
            result["wechat_added"] = 1

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
