from flask import request, redirect, g

from app import db

from config.setting import MOBILE_WHITE_LIST

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule
from app.modules.passport.register_mobile import RegisterHandler
from app.modules.base.base_handler import BaseHandler
from app.helper.response import *
from app.helper.secret import get_seed
from . import passport

from app.models.account.account_data import AccountDataModel
from app.models.account.user_access_token import UserAccessTokenModel
from app.models.account.user_sale_account import UserSaleAccountModel
from app.models.account.user_info import UserInfoModel
from app.models.account.user_id_relation import UserIdRelationModel
from app.models.account.user_account import UserAccountModel
from app.models.core.open_log import OpenLogModel


class IndexHandler(BaseHandler):

    rule = {
        "username": Rule(mobile=True),
        "code": Rule(direct_type=int),
        "country": Rule(direct_type=int, allow_empty=True, default=86)
    }

    def get(self):
        return json_fail_response(501)

    @filter_params(post=rule)
    def post(self, params):
        """
        :return:
        """
        mobile = params["username"]
        sms_code = params["code"]
        country = params["country"]

        token = request.headers.get("token")
        # 检查token不存在问题
        if not token:
            return json_fail_response(2002)

        cache_account = g.account
        # 检查用户是否被封号
        if IndexHandler.check_banned(mobile, cache_account["udid"]):
            return json_fail_response(2106)

        # 验证短信验证码
        from app.models.security.captcha import CaptchaModel
        cache_key = CaptchaModel.sms_cache_key % (mobile, "sms", country, 1)
        CaptchaModel.cache_key = cache_key
        if mobile not in MOBILE_WHITE_LIST and not CaptchaModel.verify_sms_code(sms_code):
            return json_fail_response(10001)

        account = UserAccountModel.query_account_by_mobile(mobile, country, refresh=True)
        # 当前账户不存在，则重定向到注册
        if not account:
            account = RegisterHandler.register_by_mobile(mobile, country)

        # 当前token已经绑定了一个user_id，并且绑定的用户手机号，与当前手机号不同
        if cache_account["user_id"]:
            if cache_account["mobile"] != str(mobile):
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

        if not result["password"]:
            result["perfect_info_pwd"] = 1

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

    @staticmethod
    def create_new_token_account(cache_account):
        cache_account = UserAccessTokenModel.query_useful_access_token(cache_account["access_token"])

        access_token = UserAccessTokenModel()

        # 存储客户端的基本信息
        access_token.udid = cache_account.udid
        access_token.device_type = cache_account.device_type
        access_token.version = cache_account.version
        access_token.user_agent = request.headers.get("User-Agent", "")
        access_token.ip = cache_account.ip
        access_token.status = 1
        access_token.bundle_id = cache_account.bundle_id

        # 获取生成的AccessToken和Salt
        access_token.access_token = get_seed(access_token.udid, 32)
        access_token.device_token = access_token.access_token
        access_token.salt = get_seed(access_token.udid, 10)

        # 存储到数据库
        db.session.add(access_token)
        db.session.commit()

        return access_token

    @staticmethod
    def check_banned(mobile, udid):
        """
        检查用户是否被封禁
        """
        udid_banned = UserSaleAccountModel.check_banned(mobile=None, udid=udid)
        if udid_banned:
            return True
        mobile_banned = UserSaleAccountModel.check_banned(mobile=mobile)
        if mobile_banned:
            return True
        return False


passport.add_url_rule("/loginbymobile/index", view_func=IndexHandler.as_view("index"))
