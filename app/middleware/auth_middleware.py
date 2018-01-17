"""
授权中间件，根据用户请求头中的token确认请求的用户信息
"""

from .base_middleware import BaseMiddleWare
from flask import request


class AuthMiddleWare(BaseMiddleWare):

    @staticmethod
    def before_request():
        pass

