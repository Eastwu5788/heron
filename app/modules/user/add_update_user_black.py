from flask import g
from app.modules.base.base_handler import BaseHandler
from . import user

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.account.user_black import UserBlackModel

from app.helper.auth import login_required
from app.helper.response import json_fail_response, json_success_response


class IndexHandler(BaseHandler):

    rule = {
        "black_user_id": Rule(direct_type=int),
        "status": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):

        result = UserBlackModel.update_black_status(g.account["user_id"], params["black_user_id"], params["status"])

        if not result:
            return json_fail_response(2110)

        UserBlackModel.query_black_people(g.account["user_id"], True)

        return json_success_response(result)


user.add_url_rule("/addupdateuserblack/index", view_func=IndexHandler.as_view("update_user_black_index"))