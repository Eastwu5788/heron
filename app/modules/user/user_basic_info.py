from flask import g
from . import user
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule
from app.models.account.aha_account import AhaAccountModel
from app.models.account.user_social_info import UserSocialInfoModel
from app.models.account.user_personal_info import UserPersonalInfoModel
from app.models.account.user_info import UserInfoModel
from app.models.social.social_page import SocialPageModel
from app.helper.auth import login_required
from app.helper.response import *


class IndexHandler(BaseHandler):

    @login_required
    def get(self):
        user_id = g.account["user_id"]

        result = {"user_id": user_id}

        # Aha 账号
        aha_account = AhaAccountModel.query_aha_account_by_id(user_id)
        result = dict(result, **aha_account)

        # 社交信息
        params = ["vocation_name", "school_name", "language", "emotional_state", "live_region_name"]
        user_social = UserSocialInfoModel.query_user_social_info(user_id)
        user_social_dic = user_social.format_model(params)
        print(user_social_dic)
        result = dict(result, **user_social_dic)

        # 个人信息
        params = ["weight", "height", "star_sign", "age"]
        user_personal_model = UserPersonalInfoModel.query_personal_info_by_user_id(user_id)
        user_personal_dic = user_personal_model.format_model(params)
        result = dict(result, **user_personal_dic)

        # 用户信息
        user_info_model = UserInfoModel.query_user_model_by_id(user_id)
        user_info_dic = UserInfoModel.format_user_info(user_info_model)
        result = dict(result, **user_info_dic)

        #
        social_page_dic = SocialPageModel.query_social_page_model(user_id)
        result["user_banner_type"] = social_page_dic.get("cover_type", 1)
        result["user_banner"] = social_page_dic.get("cover", "")
        if social_page_dic["cover_type"] == 2:
            result["orientation"] = social_page_dic.get("orientation", "")
            result["user_banner_cover"] = social_page_dic.get("video_img", "")

        result["album"] = UserInfoModel.query_user_album(user_id)

        return json_success_response(result)


class AlbumHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int)
    }

    @filter_params(get=rule)
    def get(self, params):

        social_page_info = SocialPageModel.query_social_page_model(params["user_id"])
        result = dict()

        result["user_banner"] = social_page_info.get("cover", "")
        result["user_banner_type"] = social_page_info.get("cover_type", 0)

        if result["user_banner_type"] == 2:
            result["orientation"] = social_page_info.get("orientation", "")
            result["user_banner_cover"] = social_page_info.get("video_img", "")

        result["album"] = UserInfoModel.query_user_album(params["user_id"])

        return result


user.add_url_rule("/userbasicinfo/index", view_func=IndexHandler.as_view("userbasic_info_index"))
user.add_url_rule("/userbasicinfo/getalbum", view_func=IndexHandler.as_view("userbasic_info_get_album"))

