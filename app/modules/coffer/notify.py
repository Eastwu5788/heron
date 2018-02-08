from . import coffer
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request import filter_params, Rule

from app.models.comment.payment_order import PaymentOrderModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.commerce.order_meta import OrderMetaModel

from app.helper.response import *


class AliHandler(BaseHandler):

    rule = {
        "notify_time": Rule(allow_empty=True),
        "notify_type": Rule(allow_empty=True),
        "notify_id": Rule(allow_empty=True),
        "sign_type": Rule(allow_empty=True),
        "sign": Rule(allow_empty=True),
        "out_trade_no": Rule(allow_empty=True),
        "subject": Rule(allow_empty=True),
        "payment_type": Rule(allow_empty=True),
        "trade_no": Rule(allow_empty=True),
        "trade_status": Rule(allow_empty=True),
        "seller_id": Rule(allow_empty=True),
        "seller_email": Rule(allow_empty=True),
        "buyer_id": Rule(allow_empty=True),
        "buyer_email": Rule(allow_empty=True),
        "total_fee": Rule(allow_empty=True),
        "quantity": Rule(allow_empty=True),
        "price": Rule(allow_empty=True),
        "body": Rule(allow_empty=True),
        "gmt_create": Rule(allow_empty=True),
        "gmt_payment": Rule(allow_empty=True),
        "is_total_fee_adjust": Rule(allow_empty=True),
        "use_coupon": Rule(allow_empty=True),
        "discount": Rule(allow_empty=True),
        "refund_status": Rule(allow_empty=True),
        "gmt_refund": Rule(allow_empty=True),
    }

    @filter_params(post=rule)
    def post(self, params):
        # 支付宝参数验证不通过
        if not PaymentOrderModel.verify_ali_order(params):
            return json_fail_response(2121)

        # 验证是否支付成功
        if not params["trade_status"] in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            return json_fail_response(2122)

        order_info = OrderInfoModel.query_order_info_with_order_no(params["out_trade_no"])
        if not order_info:
            return json_fail_response(2123)

        # 检查订单是否已经支付完成
        order_meta = OrderMetaModel.query_order_meta_with_order_id(order_info.order_id)
        if order_meta.order_status >= 2 or order_meta.pay_status in [1, 2, 4, 5, 6]:
            return json_success_response({})


    @staticmethod
    def update_order(params, order_info, meta_info):
        pass


coffer.add_url_rule("/notify/ali", view_func=AliHandler.as_view("ali_pay_notify"))