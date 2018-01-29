from . import passport
from flask import g
from app import db
from app.modules.vendor.pre_request.filter_rules import Rule
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.base.base_handler import BaseHandler

from app.models.account.user_account import UserAccountModel
from app.models.account.user_access_token import UserAccessTokenModel
from app.models.account.account_data import AccountDataModel
from app.models.account.user_id_relation import UserIdRelationModel
from app.models.core.open_log import OpenLogModel
from app.helper.response import *
from app.helper.secret import check_password

class CheckHandler(BaseHandler):
    """
    检查用户是否是老用户: /passport/login/check
    """

    rule = {
        "mobile": Rule(mobile=True, allow_empty=False),
        "country": Rule(direct_type=int, allow_empty=True, default=86)
    }

    @filter_params(get=rule)
    def get(self, params):
        result = {
            "is_new": 0,            # 是否是老用户：1是0否
            "perfect_info_pwd": 0,  # 是否需要完善密码：1是0否
        }

        mobile = params["mobile"]
        user = UserAccountModel.query_account_by_mobile(mobile, params["country"], True)

        # 1.用户是否存在 2.用户是否设置了密码
        if user:
            if not user.password:
                result["perfect_info_pwd"] = 1
        else:
            result["is_new"] = 1

        return json_success_response(result)

    def post(self):
        return json_fail_response(501)


class IndexHandler(BaseHandler):

    rule = {
        "username": Rule(mobile=True),
        "password": Rule(),
        "country": Rule(direct_type=int, allow_empty=True, default=86)
    }

    @filter_params(post=rule)
    def post(self, params):

        account = UserAccountModel.query_account_by_mobile(params["username"], params["country"])
        if not account:
            return json_fail_response(2101)

        if not check_password(account.id, params["password"], account.password):
            return json_fail_response(2104)

        # 当前token已经绑定了一个user_id，并且绑定的用户手机号，与当前手机号不同
        cache_account = g.account
        if cache_account["user_id"]:
            if cache_account["mobile"] != str(params["username"]):
                from .login_mobile import IndexHandler
                # 生成新的token
                new_access_token = IndexHandler.create_new_token_account(cache_account)
                # 禁用旧的token
                UserAccessTokenModel.forbid_by_token(cache_account["access_token"])
                # 更新内存中的数据
                cache_account["access_token"] = new_access_token.access_token
                cache_account["salt"] = new_access_token.salt

        # 执行token绑定
        UserAccessTokenModel.bind_user_id(cache_account["access_token"], account.id)
        # 刷新缓存
        result = AccountDataModel.query_request_account_by_token(cache_account["access_token"], refresh=True)
        result["perfect_info"] = 0
        result["perfect_info_pwd"] = 0

        relation = UserIdRelationModel.query_user_id_relation(account.id)
        result["huanxin_uid"] = ""
        if relation:
            result["huanxin_uid"] = relation.str_id

        if not result["gender"]:
            result["perfect_info"] = 1

        # 日活统计
        open_log = OpenLogModel()
        open_log.user_id = result.get("user_id", 0)
        open_log.udid = result.get("udid", "")
        open_log.access_token = result.get("access_token", "")
        open_log.device_type = result.get("device_type", "")
        open_log.version = result.get("version", "")
        open_log.type = 3

        db.session.add(open_log)
        db.session.commit()
        return json_success_response(result)


passport.add_url_rule("/login/check", view_func=CheckHandler.as_view("check"))
passport.add_url_rule("/login/index", view_func=IndexHandler.as_view("login_index"))
