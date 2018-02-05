import datetime
from flask import g
from . import social
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule


from app.models.base.redis import RedisModel
from app.models.social.visitor_record import VisitorRecordModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import json_success_response
from app.helper.auth import login_required


class GetListHandler(BaseHandler):

    rule = {
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        login_user_id = g.account["user_id"]

        RedisModel.reset_new_message(login_user_id, RedisModel.new_visitor)

        visitor_list = list()
        while not visitor_list:
            visitor_list = VisitorRecordModel.query_visitor_list_by_day(login_user_id, 20, params["last_id"])
            params["last_id"] += 1

            # 最多查询30天
            if params["last_id"] > 30:
                break

        visitor_dict_list = list()
        for visitor in visitor_list:
            item = dict()
            user_info = UserInfoModel.query_user_model_by_id(visitor.visitor_user_id)
            item["user_info"] = UserInfoModel.format_user_info(user_info) if user_info else {}
            item["time"] = visitor.created_time
            visitor_dict_list.append(item)

        return json_success_response({
            "last_id": params["last_id"],
            "list": visitor_dict_list
        })


social.add_url_rule("/visitor/getlist", view_func=GetListHandler.as_view("social_get_list"))
