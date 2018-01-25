from flask import g
from app import db
from app.modules.core import core

from app.modules.base.base_handler import BaseHandler

from app.models.core.open_log import OpenLogModel

from app.helper.response import *


class TouchHandler(BaseHandler):
    """
    App 初始化后，调用此接口统计用户数据
    并且返回客户端图片压缩比例
    """

    def post(self):
        open_log = OpenLogModel()
        open_log.user_id = g.account.get("user_id", 0)
        open_log.udid = g.account.get("udid", "")
        open_log.access_token = g.account.get("access_token", "")
        open_log.device_type = g.account.get("device_type", "")
        open_log.version = g.account.get("version", "")

        if open_log.device_type == 'ios':
            if open_log.user_id == 0:
                open_log.type = 1
            else:
                open_log.type = 4
        else:
            open_log.type = 4

        # 提交到数据库
        db.session.add(open_log)
        db.session.commit()

        result = {
            "avatar_comperss": 0.1,
            "dynamic_compress": 0.3,
            "chat_compress": 0.5,
            "banner_compress": 0.5,
            "private_library_compress": 0.5
        }
        return json_success_response(result)


core.add_url_rule("/openlog/touch", view_func=TouchHandler.as_view("touch"))
