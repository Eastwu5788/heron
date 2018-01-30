from flask import g
from . import user

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule, Length


from app.modules.base.base_handler import BaseHandler
from app.helper.response import *
from app.helper.auth import login_required
from app.models.account.user_info import UserInfoModel
from app.models.account.user_personal_info import UserPersonalInfoModel
from app.models.account.user_social_info import UserSocialInfoModel


class ChangeBasicInfoHandler(BaseHandler):

    rule = {
        "item": Rule(allow_empty=False),
        "nickname": Rule(allow_empty=True, length=Length(4, 8)),
        "gender": Rule(direct_type=int, allow_empty=True, enum=(1, 2)),
        "city_name": Rule(allow_empty=True),
        "vocation_name": Rule(allow_empty=True),
        "school_name": Rule(allow_empty=True),
        "language": Rule(allow_empty=True),
        "emotional_state": Rule(allow_empty=True),
        "live_region_name": Rule(allow_empty=True),
        "height": Rule(direct_type=int, allow_empty=True),
        "weight": Rule(direct_type=int, allow_empty=True),
        "star_sign": Rule(allow_empty=True),
        "age": Rule(direct_type=int, allow_empty=True),
    }

    def get(self):
        return json_fail_response(501)

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        item = params["item"]
        if item == "nickname":
            # 设置昵称，但是又没有写昵称
            if not params["nickname"]:
                return json_fail_response(5100)

            # 检查昵称被占用
            duplicated = UserInfoModel.duplicate_nick_name(nickname=params["nickname"], user_id=g.account["user_id"])
            if duplicated:
                return json_fail_response(5101)

        success = True
        if item in ["nickname", "gender", "city_name"]:
            success = UserInfoModel.update_user_info(g.account["user_id"], {item: params[item]})
        elif item in ["vocation_name", "school_name", "language", "emotional_state", "live_region_name"]:
            success = UserSocialInfoModel.update_user_social_info(g.account["user_id"], {item: params[item]})
            UserSocialInfoModel.query_user_social_info(g.account["user_id"], True)
        elif item in ["height", "weight", "star_sign", "age"]:
            success = UserPersonalInfoModel.update_user_personal_info(g.account["user_id"], {item: params[item]})

        result = {
            "data": 1 if success else 0,
            "message": "更新成功" if success else "更新失败",
        }

        return json_success_response(result)


user.add_url_rule("/changebasicinfo/index", view_func=ChangeBasicInfoHandler.as_view("index"))
