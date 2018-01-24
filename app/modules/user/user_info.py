from flask import g
from app.modules.base.base_handler import BaseHandler

from app.helper.response import *
from app.helper.auth import login_required

from app.models.account.user_info import UserInfoModel
from app.models.account.user_invite_code import UserInviteCodeModel
from . import user


user_invite_url = 'http://w.ahachat.cn/invite/invite/person?from=singlemessage&isappinstalled=1&code='


class MeHandler(BaseHandler):

    @login_required
    def get(self, *args):
        user_id = g.account["user_id"]

        user_info = UserInfoModel.query_user_model_by_id(user_id)
        if not user_info:
            return json_success_response({})

        result = dict()

        result["user_info"] = UserInfoModel.format_user_info(user_info)
        result["profit_today"] = 0
        result["ok_percent"] = UserInfoModel.calculate_ok_percent(user_id)

        invite_code = UserInviteCodeModel.query_user_invite_code(user_id)
        result["invite_url"] = user_invite_url + invite_code

        result["new_visitor"] = 0
        result["follow_add"] = 0

        result["wechat_info"] = {}

        return json_success_response(result)


user.add_url_rule("/userinfo/me", view_func=MeHandler.as_view("user_info_me"))