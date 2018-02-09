import datetime
from . import coffer
from app import db
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request import filter_params, Rule

from app.models.comment.payment_order import PaymentOrderModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.commerce.order_meta import OrderMetaModel
from app.models.coffer.payment import PaymentModel
from app.models.coffer.payment_log import PaymentLogModel
from app.models.social.share import ShareMetaModel
from app.models.base.redis import RedisModel
from app.models.social.share import ShareModel
from app.models.social.social_meta import SocialMetaModel
from app.models.social.offer import OfferModel

from app.helper.response import *
from app.common.enum_message import payment_pay_type

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

        params["pay_time"] = params["gmt_payment"]
        params["attach"] = ""
        params["message"] = params["body"]
        params["price"] = params["total_fee"] * 100

        # 更新订单信息
        AliHandler.update_order(params, order_info, order_meta)

        # 额外更新数据
        if order_meta.product_type == 80:
            AliHandler.send_remind_sms_for_wx(order_meta)
        elif order_meta.product_type == 90:


    @staticmethod
    def update_order(params, order_info, meta_info):
        # 更新OrderInfoModel
        AliHandler.update_order_info(params, order_info)
        # 更新OrderMeta
        AliHandler.update_order_meta(meta_info)
        # 更新Payment
        payment_info = AliHandler.update_payment(meta_info, order_info)

        if meta_info.share_id:
            AliHandler.update_share_meta(params, meta_info)

        # 想卖家推送新订单消息
        if meta_info.product_type in (50, 51, 60, 70, 80, 90):
            RedisModel.push_list(RedisModel.order_push_list, order_info.order_id)

        # 通知卖家有新订单消息
        if meta_info.product_type in (50, 51):
            RedisModel.add_new_message(meta_info.seller_id, RedisModel.new_order)

    @staticmethod
    def update_order_info(params, order_info):
        """
        更新订单信息
        :param params:
        :param order_info:
        :return:
        """
        order_info.pay_time = params["pay_time"]
        db.session.commit()

    @staticmethod
    def update_order_meta(meta_info):
        """
        更新订单中间信息
        """
        # 红包照片、私密视频、打赏、红包 支付完成，订单即为完成
        if meta_info.product_type in [11, 31, 40, 70]:
            meta_info.order_status = 6
            meta_info.pay_status = 1
            meta_info.ship_status = 3
        # 其它情况订单状态变更为支付完成
        else:
            meta_info.order_status = 2
            meta_info.pay_status = 1
        db.session.commit()

    @staticmethod
    def update_payment(meta_info, order_info):
        """
        更新订单支付信息
        :param meta_info:
        :param order_info:
        :return:
        """
        # 查询支付订单
        payment_info = PaymentModel.query_payment(meta_info.pay_id)

        # 变更支付订单状态
        payment_info.status = 1
        db.session.commit()

        # 插入对应的收款记录
        params = {
            "user_id": meta_info.seller_id,
            "purpose": payment_pay_type.get(order_info.order_type),
            "order_id": meta_info.order_id,
            "order_no": order_info.order_no,
            "fee_type": payment_info.fee_type,
            "total_fee": payment_info.total_fee,
            "cash_fee": payment_info.cash_fee,
            "coupon_fee": payment_info.coupon_fee,
            "coupon_count": payment_info.coupon_count,
            "pay_method": payment_info.pay_method,
            "pay_desc": payment_info.pay_desc,
            "status": 1,
        }
        PaymentModel(params)
        return payment_info

    @staticmethod
    def insert_payment_log(params, payment_info):
        """
        插入第三方交易流水
        """
        insert_params = {
            "user_id": payment_info.user_id,
            "pay_id": payment_info.pay_id,
            "channel_type": payment_info.pay_method,
            "transaction_type": "PAY",
            "transaction_id": params["trade_no"],
            "transaction_fee": payment_info.total_fee,
            "trade_success": 1,
            "optional": params["attach"],
            "message_detail": params.get("message", "")
        }
        PaymentLogModel(params=insert_params)

    @staticmethod
    def update_share_meta(params, meta_info):
        share_meta = ShareMetaModel.query_share_meta_model(meta_info.share_id)
        if not share_meta:
            share_meta = ShareMetaModel()
            share_meta.share_id = meta_info.share_id
            share_meta.user_id = meta_info.seller_id
            share_meta.reward = 1
            share_meta.reward_money = params["price"]

            db.session.add(share_meta)
        else:
            share_meta.reward += 1
            share_meta.reward_money += params["price"]

        db.session.commit()
        return share_meta

    @staticmethod
    def send_remind_sms_for_wx(meta_info):
        """
        微信出售后，给卖家一个短信提醒
        """
        pass

    @staticmethod
    def update_offer(params, meta_info):
        """
        更新悬赏信息
        """
        # 更新悬赏动态，悬赏付过钱后才真正发布成功
        ShareModel.query.filter_by(share_id=meta_info.share_id).update(dict(status=1))
        # 更新用户动态统计数字
        SocialMetaModel.update_social_meta_model(meta_info.buyer_id, ["share"])

        offer_update = {
            "status": 1,
            "offer_status": 2,
            "start_time": params["pay_time"],
            "due_time": (datetime.datetime.strptime(params["pay_time"]) + datetime.timedelta(seconds=86400)).strftime("%Y-%m-%d %H:%M:%S")
        }
        OfferModel.query.filter_by(share_id=meta_info.share_id).update(offer_update)





coffer.add_url_rule("/notify/ali", view_func=AliHandler.as_view("ali_pay_notify"))