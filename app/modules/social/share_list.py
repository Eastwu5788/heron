from flask import g
from . import social
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule
from app.models.social.share import ShareModel
from app.helper.response import json_success_response


class IndexHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):
        login_user_id = g.account["user_id"]

        is_self = params["user_id"] == login_user_id

        share_model_list = ShareModel.query_user_share_list(params["user_id"] if not is_self else None, login_user_id if is_self else 0, 20, params["last_id"])
        result = ShareModel.format_share_model(share_model_list, login_user_id)
        return json_success_response(result)


social.add_url_rule("/sharelist/index", view_func=IndexHandler.as_view("share_list_index"))