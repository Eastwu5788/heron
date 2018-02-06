from flask import g
from . import user
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.filter_rules import Rule
from app.modules.vendor.pre_request.flask import filter_params

from app.models.social.follow import FollowModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import *
from app.helper.utils import array_column
from app.helper.auth import login_required


class GetListHandler(BaseHandler):

    per_page = 20

    rule = {
        "user_id": Rule(direct_type=int),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0),
        "type": Rule(direct_type=int, allow_empty=True, enum=(2, 3, 4))   # 2关注 3粉丝 4好友
    }

    @filter_params(get=rule)
    def get(self, params):
        params["limit"] = self.per_page

        user_list = []
        field = ""
        # 关注
        if params["type"] == 2:
            user_list = FollowModel.query_follow_list(params)
            field = "follow_id"
        # 粉丝
        elif params["type"] == 3:
            user_list = FollowModel.query_fans_list(params)
            field = "user_id"
        # 好友
        elif params["type"] == 4:
            user_list = FollowModel.query_friends_list(params)
            field = "follow_id"
        if not user_list:
            return json_success_response(user_list)

        other_user_id_list = array_column(user_list, field)
        user_relations_dict = FollowModel.query_relation_to_user_list(g.account["user_id"], other_user_id_list)

        result = list()
        for follow_model in user_list:
            item = dict()
            item["id"] = follow_model.id
            user_id = getattr(follow_model, field)
            item["relation_type"] = user_relations_dict.get(user_id, 0)
            user_model = UserInfoModel.query_user_model_by_id(user_id)
            item["user_info"] = UserInfoModel.format_user_info(user_model)
            result.append(item)

        return json_success_response(result)


class FriendStatusHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        relation = FollowModel.query_relation_to_user(g.account["user_id"], params["user_id"])
        return json_success_response({"data": relation})


user.add_url_rule("/friends/getlist", view_func=GetListHandler.as_view("friends_get_list"))
user.add_url_rule("/friends/getfriendstatus", view_func=FriendStatusHandler.as_view("get_friend_status"))
