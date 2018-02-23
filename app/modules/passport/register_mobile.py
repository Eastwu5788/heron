import re
from flask import request, g

from . import passport

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule, Length

from app import db
from app.helper.response import *
from app.modules.base.base_handler import BaseHandler

from app.models.account.user_account import UserAccountModel
from app.models.account.user_info import UserInfoModel
from app.models.account.user_personal_info import UserPersonalInfoModel
from app.models.account.aha_account import AhaAccountModel
from app.models.account.user_social_info import UserSocialInfoModel
from app.models.account.user_id_relation import UserIdRelationModel
from app.helper.secret import generate_password, md5


class RegisterHandler(BaseHandler):

    @staticmethod
    def register_by_mobile(mobile, country):
        # 注册一个新的账户
        account = UserAccountModel()
        account.username = mobile
        account.mobile = mobile
        account.country = country

        db.session.add(account)
        db.session.commit()

        # 使用事务提交默认参数
        user_info = UserInfoModel()
        user_info.user_id = account.id
        user_info.nickname = "Aha" + str(account.id)

        # 私人信息
        user_personal_info = UserPersonalInfoModel()
        user_personal_info.user_id = account.id
        user_personal_info.age = 16

        # Aha账户
        aha_account = AhaAccountModel()
        aha_account.user_id = account.id
        aha_account.aha_id = 1000000 + account.id
        aha_account.changeable_aha = 1

        # 社交信息
        user_social = UserSocialInfoModel()
        user_social.user_id = account.id
        user_social.language = "中文"
        user_social.emotional_state = "保密"
        user_social.live_region_name = "中国"

        # 环信账号
        from heron import app
        user_id_relation = UserIdRelationModel()
        user_id_relation.user_id = account.id
        user_id_relation.str_id = md5(str(account.id))  # md5(app.config["CACHE_KEY_PREFIX"] + str(account.id))

        # 提交到数据库
        db.session.add(user_info)
        db.session.add(user_personal_info)
        db.session.add(aha_account)
        db.session.add(user_social)
        db.session.add(user_id_relation)
        db.session.commit()

        return account


class GeneratePasswordHandler(BaseHandler):

    rule = {
        'password': Rule()
    }

    def get(self):
        return json_fail_response(501)

    @filter_params(post=rule)
    def post(self, params):
        account = g.account
        if not account:
            return json_fail_response(503)

        password = params["password"]

        if len(password) != 6:
            return json_fail_response(2017)

        if not re.match(r"[a-zA-Z0-9]{6}", password):
            return json_fail_response(2018)

        password = generate_password(account["user_id"], password)
        UserAccountModel.update_account_password(account["user_id"], account["mobile"], account["country"], password)
        return json_success_response()


passport.add_url_rule("/register/setpassword", view_func=GeneratePasswordHandler.as_view("setpassword"))
