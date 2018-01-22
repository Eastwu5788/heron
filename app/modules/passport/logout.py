from flask import g, request
from app import db
from . import passport
from app.modules.base.base_handler import BaseHandler
from app.helper.response import *
from app.helper.auth import login_required
from app.helper.secret import get_seed
from app.models.account.user_access_token import UserAccessTokenModel
from app.models.account.account_data import AccountDataModel


class LogoutHandler(BaseHandler):

    def get(self):
        json_fail_response(501)

    @login_required
    def post(self):
        result = LogoutHandler.generate_new_token(g.account)
        if not result:
            return json_fail_response(2103)

        # 禁用旧的token
        old_token = g.account.get("token")

        UserAccessTokenModel.forbid_by_token(old_token)
        AccountDataModel.query_request_account_by_token(old_token, refresh=True)

        # 更新新的token
        result = AccountDataModel.query_request_account_by_token(result.access_token)
        return json_success_response(result)

    @staticmethod
    def generate_new_token(account):
        if not account:
            return False
        access_token = UserAccessTokenModel()

        # 存储客户端的基本信息
        access_token.udid = account["udid"]
        access_token.device_type = account["device_type"]
        access_token.version = account["version"]
        access_token.user_agent = request.headers.get("User-Agent", "")
        access_token.ip = request.remote_addr
        access_token.status = 1
        access_token.bundle_id = account["bundle_id"]

        # 获取生成的AccessToken和Salt
        access_token.access_token = get_seed(account["udid"], 32)
        access_token.device_token = access_token.access_token
        access_token.salt = get_seed(account["udid"], 10)

        # 存储到数据库
        db.session.add(access_token)
        try:
            db.session.commit()
            return access_token
        except:
            db.session.rollback()
            return False


passport.add_url_rule("/logout/index", view_func=LogoutHandler.as_view("lougout.index"))
