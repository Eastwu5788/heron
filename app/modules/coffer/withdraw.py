from flask import g
from . import coffer
from app.modules.base.base_handler import BaseHandler

from app.models.coffer.wallet_info import WalletInfoModel
from app.models.coffer.withdraw_info import WithdrawInfoModel
from app.models.coffer.withdraw_oauth_account import WithdrawOauthAccountModel
from app.modules.vendor.pre_request import filter_params, Rule
from app.helper.auth import login_required
from app.helper.response import *


class MoneyHandler(BaseHandler):

    @login_required
    def get(self):

        result = {
            "balance": 0,
            "withdraw_type": 4,     # 1.微信 2.支付宝 3.银行账户 4.微信企业支付 5.支付宝企业支付
            "can_withdraw": 0,      # 1.可提现 0.不可提现
            "bind_acount": 1,       # 0.不需要绑定第三方账户 1.不需要绑定企业账户
            "message": "可以提现",
        }

        wallet = WalletInfoModel.query_wallet(g.account["user_id"])
        if not wallet:
            result["message"] = "无可提现金额"
            return json_success_response(result)
        result["balance"] = wallet.balance_useable / 100

        withdraw_enable = WithdrawInfoModel.check_withdraw_enable(g.account["user_id"])
        if not withdraw_enable:
            result["message"] = "一天只能体现一次"
            return json_success_response(result)

        if result["balance"] < 1:
            result["message"] = "可提现金额不足(1元)"
            return json_success_response(result)

        oauth_account = WithdrawOauthAccountModel.query_withdraw_oauth_account(g.account["user_id"], 1)
        result["bind_acount"] = 1 if oauth_account else 0

        result["can_withdraw"] = 1
        return json_success_response(result)


class InfoListHandler(BaseHandler):

    rule = {
        "last_id": Rule(direct_type=int, allow_empty=True, default=0),
        "type": Rule(direct_type=int, enum=[0, 1, 2])
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        # 显示提现中
        if params["type"] == 1:
            params["status"] = [1, 2]
        # 显示已提现
        elif params["type"] == 2:
            params["status"] = 3

        result = WithdrawInfoModel.query_withdraw_info_list(g.account["user_id"], params)
        return json_success_response(result)


coffer.add_url_rule("/withdraw/getmoney", view_func=MoneyHandler.as_view("withdraw_getmoney"))
coffer.add_url_rule("/withdraw/getInfoList", view_func=InfoListHandler.as_view("withdraw_getinfolist"))
