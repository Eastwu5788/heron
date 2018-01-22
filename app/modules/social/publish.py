from . import social
from app.helper.auth import login_required
from app.helper.response import *
from app.modules.base.base_handler import BaseHandler


class KindHandler(BaseHandler):

    def post(self):
        return json_fail_response(501)

    @login_required
    def get(self):
        result = [
            {
                "type": 2,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售照片",
            },
            {
                "type": 3,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售视频",
            },
            {
                "type": 4,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售微信",
            },
            {
                "type": 1,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "发布动态",
            },
            {
                "type": 5,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "发布悬赏",
            },
            {
                "type": 6,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "邀请奖励",
            }
        ]
        return json_success_response(result)


social.add_url_rule("/publish/kind", view_func=KindHandler.as_view("kind"))
