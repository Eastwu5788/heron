from flask import g
from app import redis
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.modules.base.base_handler import BaseHandler

from app.helper.response import *
from app.helper.auth import login_required

from app.models.account.user_info import UserInfoModel
from app.models.account.user_invite_code import UserInviteCodeModel
from app.models.social.social_meta import SocialMetaModel
from app.models.social.social_page import SocialPageModel
from app.models.coffer.user_profit import UserProfitModel
from app.models.account.user_location import UserLocationModel
from app.models.account.aha_account import AhaAccountModel
from app.models.social.share import ShareModel
from app.models.core.open_log import OpenLogModel
from app.models.social.visitor_record import VisitorRecordModel
from app.models.base.redis import RedisModel
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

        result["new_visitor"] = RedisModel.query_new_message(user_id, RedisModel.new_visitor)
        result["follow_add"] = 0

        result["wechat_info"] = {}
        return json_success_response(result)


class IndexHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):

        if params["user_id"] == 0:
            return json_fail_response(2101)

        user_info = UserInfoModel.query_user_model_by_id(params["user_id"])
        result = UserInfoModel.format_user_info(user_info)

        social_meta_info = SocialMetaModel.query_social_meta_info(params["user_id"])
        result["share_num"] = social_meta_info.share if social_meta_info else 0
        result["follow_num"] = social_meta_info.following if social_meta_info else 0
        result["fans_num"] = social_meta_info.follower if social_meta_info else 0
        result["follow_status"] = 1
        result["album"] = []

        social_page_info = SocialPageModel.query_social_page_model(params["user_id"])
        result["user_banner"] = social_page_info.get("cover", "")
        result["user_banner_type"] = social_page_info.get("cover_type", 1)

        if result["user_banner_type"] == 2:
            result["orientation"] = ""
            result["user_banner_cover"] = ""

        if params["user_id"] == g.account["user_id"]:
            result["profit"] = IndexHandler.query_user_profit(params["user_id"])

        if result["identified"] == 1:
            result["identify_title"] = "官方认证：" + result["identify_title"]

        user_location = UserLocationModel.query.filter(UserLocationModel.id == user_info.location_id).first()
        result["latitude"] = user_location.latitude if user_location else 0
        result["longitude"] = user_location.longitude if user_location else 0

        result["changeable_aha"] = 1
        result["aha_id"] = ''

        aha_info = AhaAccountModel.query_aha_account_by_id(params['user_id'], auto_formated=False)
        if aha_info:
            result["changeable_aha"] = aha_info.changeable_aha
            if aha_info.changeable_aha == 0:
                result["aha_id"] = aha_info.aha_id

        # 最近的动态
        result["share_info"] = ShareModel.query_recent_share_photo(params['user_id'], g.account["user_id"])
        # 是否有交易记录
        result["had_trade"] = 1
        # 备注昵称
        result["remark_name"] = ""

        last_login = OpenLogModel.query_last_login(params["user_id"])
        result["last_login"] = 0
        if last_login:
            result["last_login"] = time.time() - time.mktime(last_login.created_time.timetuple())

        # 插入访客记录
        if g.account["user_id"] != 0 and g.account["user_id"] != params["user_id"]:
            RedisModel.add_new_message(params["user_id"], RedisModel.new_visitor)
            VisitorRecordModel(user_id=params["user_id"], visitor_user_id=g.account["user_id"])

        return json_success_response(result)

    @staticmethod
    def query_user_profit(user_id):
        user_profit = UserProfitModel.query_user_profit(user_id)

        result = {
            "all_money": user_profit.money if user_profit else 0,
            "today_money": user_profit.today_money if user_profit else 0,
        }
        return result


user.add_url_rule("/userinfo/me", view_func=MeHandler.as_view("user_info_me"))
user.add_url_rule("/userinfo/index", view_func=IndexHandler.as_view("user_info_index"))
