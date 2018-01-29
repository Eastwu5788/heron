from . import social
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.like import LikeModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):
        query = LikeModel.query.filter_by(share_id=params["share_id"], status=1)
        if params["last_id"]:
            query = query.filter(LikeModel.like_id < params["last_id"])
        like_model_list = query.order_by(LikeModel.like_id.desc()).limit(20).all()

        result = list()

        for model in like_model_list:
            user_info = UserInfoModel.query_user_model_by_id(model.user_id)
            user_info = UserInfoModel.format_user_info(user_info)
            user_info["like_id"] = model.like_id
            result.append(user_info)

        return json_success_response(result)


social.add_url_rule("/getlikelist/index", view_func=IndexHandler.as_view("get_like_list_index"))
