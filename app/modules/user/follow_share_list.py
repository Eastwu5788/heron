from flask import g
from . import user

from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule
from app.models.social.follow import FollowModel
from app.models.social.share import ShareModel
from app.helper.auth import login_required
from app.helper.response import json_success_response


class IndexHandler(BaseHandler):

    rule = {
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):

        user_id = g.account["user_id"]

        follow_user_id_list = FollowModel.query_follow_user_list(user_id)
        follow_user_id_list = list(set(follow_user_id_list))
        share_model_list = ShareModel.query_user_share_list(follow_user_id_list, user_id, 20, params["last_id"], 0)
        share_info_list = ShareModel.format_share_model(share_model_list, user_id)
        return json_success_response(share_info_list)


user.add_url_rule("/getfollowsharelist/index", view_func=IndexHandler.as_view("follow_share_list_index"))
