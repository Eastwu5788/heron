"""
加密校验中间件
请求中间件：根据请求Body中的内容判断用户请求是否合法
响应中间件：对响应的result中的数据执行加密操作
"""
from flask import request

from .base_middleware import BaseMiddleWare
from app.helper.response import json_fail_response
from app.helper.secret import generate_request_sign


class SecretMiddleWare(BaseMiddleWare):

    @staticmethod
    def before_request():
        # 当前接口是否需要进行安全检查
        from config.setting import REQUEST_SECRET_CHECK, WHITE_LIST
        if not REQUEST_SECRET_CHECK or request.path in WHITE_LIST:
            return

        # 查询salt
        salt = ""
        sign = generate_request_sign(request.values.items(), salt)

        # 参数校验不通过
        if request.headers.get("sign", "") != sign:
            return json_fail_response(502)

    @staticmethod
    def after_request(response):
        """
        请求结果加密
        """
        return response
