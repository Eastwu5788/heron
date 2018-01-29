from flask import g
from . import social
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.share import ShareModel
from app.models.social.like import LikeModel

from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
    }

    @filter_params(get=rule)
    def get(self, params):
        share_model = ShareModel.query_share_model(params["share_id"])
        if not share_model:
            return json_fail_response(2405)

        share_info = ShareModel.format_share_model([share_model], g.account["user_id"])[0]
        like_list = LikeModel.query_like_list(params["share_id"], 0)
        share_info["like_list"] = like_list

        del share_info["price"]
        del share_info["product_id"]

        return json_success_response(share_info)


social.add_url_rule("/sharedetail/index", view_func=IndexHandler.as_view("share_detail_index"))
