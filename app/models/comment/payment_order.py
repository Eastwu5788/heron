"""
WeXin: https://github.com/zwczou/weixin-python
AliPay: https://github.com/fzlee/alipay
"""
from app.modules.vendor.weixin import WeixinPay, WeixinError
from app.modules.vendor.alipay import AliPay
from app.models.commerce.order_info import OrderInfoModel


class PaymentOrderModel(object):

    wx_notify_url = "/coffer/notify/weixin"
    ali_notify_url = "/coffer/notify/ali"

    @staticmethod
    def load_config_params():
        """
        加载配置项参数
        """
        from heron import app

        params = dict()

        # 加载微信支付参数
        params["wx_app_id"] = app.config.get("WX_APP_ID", "")
        params["wx_mch_id"] = app.config.get("WX_MCH_ID", "")
        params["wx_mch_key"] = app.config.get("WX_MCH_KEY", "")
        params["wx_notify_url"] = PaymentOrderModel.wx_notify_url

        # 加载支付宝支付参数
        params["ali_app_id"] = app.config.get("ALI_APP_ID", "")
        params["ali_partner_id"] = app.config.get("ALI_PARTNER_ID", "")
        params["ali_seller_id"] = app.config.get("ALI_SELLER_ID", "")
        params["ali_key"] = app.config.get("ALI_KEY", "")
        params["ali_sign_type"] = app.config.get("ALI_KEY", "")
        params["ali_private_key_path"] = app.config.get("ALI_PRIVATE_KEY_PATH", "")
        params["ali_public_key_path"] = app.config.get("ALI_PUBLIC_KEY_PATH", "")
        params["ali_cacert_path"] = app.config.get("ALI_CACERT_PATH", "")
        params["ali_notify_url"] = PaymentOrderModel.ali_notify_url

        return params

    @staticmethod
    def generate_wx_order(params):
        """
        微信下订单
        :param params:
        :return:
        """
        config = PaymentOrderModel.load_config_params()

        wx_pay = WeixinPay(config["wx_app_id"], config["wx_mch_id"], config["wx_mch_key"], config["wx_notify_url"])

        order_info = {
            "total_fee": str(int(params["price"] * 100)),
            "trade_type": "APP",
            "body": params["pro_name"],
            "out_trade_no": params["order_no"]
        }

        try:
            prepay_id = wx_pay.unified_order(**order_info).get("prepay_id", "")
        except WeixinError as e:
            return False, 2120

        if not prepay_id:
            order_info = OrderInfoModel.query.filter_by(order_no=params["order_no"]).first()
            prepay_id = order_info.transaction_id

        pay_params = wx_pay.config_for_app_payment(prepay_id)
        pay_params["out_trade_no"] = params["order_no"]
        return True, pay_params

    @staticmethod
    def generate_ali_order(params):
        """
        支付宝下单
        :param params: 订单参数
        """
        config = PaymentOrderModel.load_config_params()
        app_private_key_string = open(config["ali_private_key_path"]).read()
        alipay_public_key_string = open(config["ali_public_key_path"]).read()

        app_private_key_string == """
                -----BEGIN RSA PRIVATE KEY-----
                base64 encoded content
                -----END RSA PRIVATE KEY-----
                """

        alipay_public_key_string == """
                -----BEGIN PUBLIC KEY-----
                base64 encoded content
                -----END PUBLIC KEY-----
            """

        alipay = AliPay(config["ali_app_id"], config["ali_notify_url"],
                        app_private_key_string, alipay_public_key_string,
                        config["ali_sign_type"])

        order_string = alipay.api_alipay_trade_app_pay(
            out_trade_no=params["order_no"],
            total_amount=str(int(params["price"] * 100)),
            subject=params["pro_name"]
        )
        return True, {"url": order_string, "out_trade_no": params["order_no"]}
