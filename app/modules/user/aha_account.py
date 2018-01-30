from flask import g
from . import user

from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule, Length

from app.models.account.aha_account import AhaAccountModel

from app.helper.response import *
from app.helper.auth import login_required


class ChangeHandler(BaseHandler):

    rule = {
        "aha_id": Rule(length=Length(5, 20))
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        check_result = AhaAccountModel.check(params["aha_id"])
        if not check_result["success"]:
            return json_fail_response(2107, check_result["message"])

        account = AhaAccountModel.query_aha_account_by_aha_id(params["aha_id"])
        if account and account.changeable_aha == 0:
            return json_fail_response(2108)

        result = AhaAccountModel.update_aha_id(g.account["user_id"], params["aha_id"])
        if result:
            return json_success_response({
                "data": 1,
                "message": "设置成功"
            })
        else:
            return json_success_response({
                "data": 0,
                "message": "设置失败"
            })


user.add_url_rule("/ahaaccount/change", view_func=ChangeHandler.as_view("aha_account_change"))
