from flask import g
from app.helper.response import *


def login_required(func):
    """
    登录权限检查装饰器
    """
    def check_auth(*args, **kwargs):
        print(g.account)
        if not g.account or not g.account.get("user_id"):
            return json_fail_response(2102)
        return func(*args, **kwargs)
    return check_auth
