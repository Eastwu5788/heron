from collections import OrderedDict
from flask import g
from . import coffer

from app import db

from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.account.user_black import UserBlackModel
from app.models.account.user_info import UserInfoModel
from app.models.account.user_address import UserAddressModel
from app.models.account.user_wechat import UserWeChatModel
from app.models.social.share import ShareModel
from app.models.social.image import ImageModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.coffer.payment import PaymentModel
from app.models.commerce.order_meta import OrderMetaModel
from app.models.commerce.order_user_status import OrderUserStatusModel
from app.models.comment.payment_order import PaymentOrderModel

from app.helper.auth import login_required
from app.helper.response import *
from app.helper.secret import *

from app.common.enum_message import payment_type_message


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int, allow_empty=True, default=0),
        "user_id": Rule(direct_type=int),
        "type_id": Rule(direct_type=int, enum=[11, 70, 40, 50, 51, 80, 90]),
        "channel_type": Rule(direct_type=int),
        "price": Rule(direct_type=float),
        "consignee": Rule(allow_empty=True, default=""),            # 收货人
        "mobile": Rule(allow_empty=True, default="", mobile=True),
        "address_name": Rule(allow_empty=True),                     # 收货地址
        "email": Rule(allow_empty=True, default="", email=True),
        "message": Rule(allow_empty=True, default="")               # 留言
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        # 拉黑过滤
        user_black_status = UserBlackModel.check_black_status(g.account["user_id"], params["user_id"])
        if user_black_status != 0:
            return json_fail_response(2111)

        # 生成订单信息
        success, result = IndexHandler.generate_base_order_info(params)
        if not success:
            return json_fail_response(result)

        # 创建订单
        result = IndexHandler.generate_order(params, result)
        success, result = IndexHandler.generate_payment_params(params, result["payment_param"], result["order_info"])

        if not success:
            return json_fail_response(result)

        return json_success_response(result)

    @staticmethod
    def generate_payment_params(params, payment_param, order_info):
        result = {}
        # 生成微信订单数据
        if params["channel_type"] == 1:
            success, result = PaymentOrderModel.generate_wx_order(payment_param)
            if not success:
                return False, result

            if result.get("prepayid", None):
                OrderInfoModel.query.filter_by(order_id=order_info.get("order_id")).update(dict(transaction_id=result["prepayid"]))
                db.session.commit()

        # 生成支付宝订单数据
        elif params["channel_type"] == 2:
            success, result = PaymentOrderModel.generate_ali_order(payment_param)

        return True, result

    @staticmethod
    def generate_order(params, order_meta):
        # 生成订单信息
        order_info = {
            "order_price": order_meta["price"],
            "order_no": generate_order_id(),
            "order_fee": order_meta["price"],
            "order_type": params["type_id"],
            "order_message": params.get("message", ""),
            "address_id": order_meta.get("address_id", 0)
        }
        order_model = OrderInfoModel(params=order_info)
        order_dict = order_model.to_dict()

        # 创建payment
        payment_info = {
            "user_id": g.account["user_id"],
            "purpose": params["type_id"],
            "order_id": order_model.order_id,
            "order_no": order_model.order_no,
            "pay_method": params["channel_type"],
            "total_fee": order_model.order_fee,
            "status": 3,
            "fee_type": "CNY"
        }
        payment_model = PaymentModel(payment_info)
        order_dict["pay_id"] = payment_model.pay_id

        order_meta_info = {
            "buyer_id": g.account["user_id"],
            "seller_id": order_meta.get("seller_id", 0),
            "share_id": order_meta.get("share_id"),
            "order_type": params["type_id"],
            "order_id": order_model.order_id,
            "product_type": params["type_id"],
            "order_status": 1,
            "pay_status": 3,
            "pay_id": payment_model.pay_id,
            "product_id": order_meta.get("product_id", 0)
        }
        order_meta_model = OrderMetaModel(order_meta_info)

        payment_params = {
            "price": order_meta["price"] / 100,
            "order_no": order_model.order_no,
            "pro_name": payment_type_message[params["type_id"]]
        }

        order_user_status = {
            "user_id": g.account["user_id"],
            "status": 1,
            "order_id": order_model.order_id,
        }
        OrderUserStatusModel(params=order_user_status)

        if params["type_id"] != 90:
            order_user_status["user_id"] = order_meta_model.seller_id
            OrderUserStatusModel(params=order_user_status)

        return {"payment_param": payment_params, "order_info": order_dict}

    @staticmethod
    def generate_base_order_info(params):
        """
        生成基础订单信息
        :param params: 请求参数
        """
        order_meta = dict()

        # 红包照片
        if params["type_id"] == 11:
            # 动态被删除或不存在
            order_meta = IndexHandler.check_share_info(params["share_id"])
            if not order_meta:
                return False, 2112
            order_meta["price"] = IndexHandler.check_share_image_price(params["share_id"], params["user_id"])

        # 打赏
        elif params["type_id"] == 70:
            # 请求参数错误
            if not params["price"] or not params["user_id"]:
                return False, 2113

            # 打赏金额过少
            if params["price"] < 1:
                return False, 2114

            order_meta["seller_id"] = params["user_id"]
            order_meta["share_id"] = 0
            order_meta["price"] = params["price"] * 100

        # 商品
        elif params["type_id"] == 50 or params["type_id"] == 51:
            order_meta = IndexHandler.check_share_info(params["share_id"])
            if not order_meta:
                return False, 2112

            # 生成商品地址信息
            success, result = IndexHandler.generate_consignee(params)
            if not success:
                return False, result

            order_meta["address_id"] = result

        # 微信号
        elif params["type_id"] == 80:
            wechat_model = UserWeChatModel.query_user_wechat_model(params["user_id"])
            if not wechat_model:
                return False, 2119
            order_meta["seller_id"] = wechat_model.user_id
            order_meta["price"] = wechat_model.price

        return True, order_meta

    @staticmethod
    def check_share_info(share_id):
        order_meta = dict()
        share_model = ShareModel.query_share_model(share_id)
        if share_model:
            order_meta["seller_id"] = share_model.user_id
            order_meta["share_id"] = share_model.share_id
            order_meta["price"] = share_model.price
            order_meta["product_id"] = share_model.product_id
            order_meta["user_id"] = share_model.user_id
        return order_meta

    @staticmethod
    def check_share_image_price(share_id, user_id):
        share_image_list = ImageModel.query_share_images(share_id)
        user_info = UserInfoModel.query_user_model_by_id(user_id)

        # 认证用户每张照片1块钱， 普通用户每张照片5毛
        image_count = len(share_image_list)
        if user_info.identified == 1:
            return image_count * 100
        else:
            return image_count * 0.5 * 100

    @staticmethod
    def generate_consignee(params):
        if not params["consignee"]:
            return False, 2115

        if params["type_id"] == 51:
            if not params["email"]:
                return False, 2116

        if not params["mobile"]:
            return False, 2117

        query_params = OrderedDict()
        query_params["email"] = params["email"]
        query_params["mobile"] = params["mobile"]
        query_params["address"] = params["address"]
        query_params["consignee"] = params["consignee"]
        old_address = UserAddressModel.query_user_address(params["user_id"], query_params)
        if not old_address:
            query_params["user_id"] = params["user_id"]
            try:
                old_address = UserAddressModel(params=query_params)
            except:
                return False, 2118
        return True, old_address.id


coffer.add_url_rule("/order/index", view_func=IndexHandler.as_view("order_index"))
