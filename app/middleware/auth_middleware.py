"""
授权中间件，根据用户请求头中的token确认请求的用户信息
"""

from .base_middleware import BaseMiddleWare
from flask import request, g


class AuthMiddleWare(BaseMiddleWare):

    @staticmethod
    def before_request():
        """
        授权验证中间件
        存储当前登录用户信息
        """
        from app.models.account.account_data import AccountDataModel
        token = request.headers.get("token")
        result = dict()
        if token:
            result = AccountDataModel.query_request_account_by_token(token)
            result["token"] = token
        g.account = result
