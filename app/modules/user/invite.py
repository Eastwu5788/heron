from flask import g
from . import user
from app.modules.base.base_handler import BaseHandler

from app.models.account.user_invite_code import UserInviteCodeModel

from app.helper.auth import login_required
from app.helper.response import *


class IndexHandler(BaseHandler):

    @login_required
    def get(self):
        code = UserInviteCodeModel.query_user_invite_code(g.account["user_id"])

        invite_info = dict()
        invite_info["url"] = 'http://w.ahachat.cn/invite/invite/person?from=singlemessage&isappinstalled=1&code=' + code
        invite_info["proportion"] = "20%"
        invite_info["invite_num"] = 0
        invite_info["invite_income"] = 0

        return json_success_response(invite_info)


user.add_url_rule("/invite/index", view_func=IndexHandler.as_view("invite_index"))
