from heron import app

from app.helper.wx_pay import WxPay


class PaymentOrderModel(object):

    wx_notifi_url = "/coffer/notify/weixin"
    ali_notifi_url = "/coffer/notify/ali"

    @staticmethod
    def wechat_order(params):
        """
        微信下订单
        :param params:
        :return:
        """
        wx_app = WxPay()