from . import passport

from app.modules.vendor.pre_request.filter_rules import Rule
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.base.base_handler import BaseHandler

from app.models.account.user_account import UserAccountModel

from app.helper.response import *


class CheckHandler(BaseHandler):
    """
    检查用户是否是老用户: /passport/login/check
    """

    rule = {
        "mobile": Rule(mobile=True, allow_empty=False),
        "country": Rule(direct_type=int, allow_empty=True, default=86)
    }

    @filter_params(get=rule)
    def get(self, params):
        result = {
            "is_new": 0,            # 是否是老用户：1是0否
            "perfect_info_pwd": 0,  # 是否需要完善密码：1是0否
        }

        mobile = params["mobile"]
        user = UserAccountModel.query_account_by_mobile(mobile, params["country"], True)

        # 1.用户是否存在 2.用户是否设置了密码
        if user:
            if not user.password:
                result["perfect_info_pwd"] = 1
        else:
            result["is_new"] = 1

        return json_success_response(result)

    def post(self):
        return json_fail_response(501)


passport.add_url_rule("/login/check", view_func=CheckHandler.as_view("check"))
