from flask import g
from . import user

from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule, Length

from app.models.account.aha_account import AhaAccountModel
from app.models.account.user_black import UserBlackModel
from app.models.account.user_info import UserInfoModel
from app.models.account.user_id_relation import UserIdRelationModel

from app.helper.response import *
from app.helper.auth import login_required
from app.helper.utils import array_column


class IndexHandler(BaseHandler):

    per_page = 20

    rule = {
        "limit": Rule(direct_type=int, allow_empty=True, default=1)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        offset = IndexHandler.per_page * params["limit"]
        user_black_list = UserBlackModel.query_user_black_list(g.account["user_id"], 1, offset, IndexHandler.per_page)

        user_id_list = array_column(user_black_list, "black_user_id")

        result = list()

        for user_id in user_id_list:

            user_info = UserInfoModel.query_user_model_by_id(user_id)
            if not user_info:
                continue
            item = dict()
            item["user_id"] = user_info.user_id
            item["nickname"] = user_info.nickname

            item["avatar"] = UserInfoModel.format_user_avatar(user_info)
            user_id_relation = UserIdRelationModel.query_user_id_relation(user_info.user_id)
            item["huanxin_uid"] = user_id_relation.str_id if user_id_relation else ""
            result.append(item)

        return json_success_response(result)


class BlackStatusHandler(BaseHandler):

    rule = {
        "black_user_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        code = UserBlackModel.check_black_status(g.account["user_id"], params["black_user_id"])
        result = {
            "data": code,
            "message": "无拉黑关系"
        }

        if code == 1:
            result["message"] = "我把它拉黑"
        elif code == 2:
            result["message"] = "他把我拉黑"
        elif code == 3:
            result["message"] = "已互相拉黑"

        return json_success_response(result)




user.add_url_rule("/getuserblack/index", view_func=IndexHandler.as_view("get_user_black_index"))
user.add_url_rule("/checkisblack/getblackstatus", view_func=BlackStatusHandler.as_view("get_black_status"))
