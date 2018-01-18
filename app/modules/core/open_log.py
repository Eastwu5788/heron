from app.modules.core import core

from app.modules.base.base_handler import BaseHandler
from app.helper.response import *


class TouchHandler(BaseHandler):
    """
    App 初始化后，调用此接口统计用户数据
    并且返回客户端图片压缩比例
    """

    def get(self):
        return json_fail_response(501)

    def post(self):
        result = {
            "avatar_comperss": 0.1,
            "dynamic_compress": 0.3,
            "chat_compress": 0.5,
            "banner_compress": 0.5,
            "private_library_compress": 0.5
        }
        return json_success_response(result)


core.add_url_rule("/openlog/touch", view_func=TouchHandler.as_view("touch"))
