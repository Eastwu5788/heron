from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.modules.core import core
from app.modules.base.base_handler import BaseHandler

from app.models.core.app_version import AppVersionModel

from app.helper.response import *

"""
core/appversion/isopen
core/appversion/getversion
通用规则
"""
rule = {
        "version": Rule(allow_empty=False),
        "device_type": Rule(allow_empty=False)
}


class OpenHandler(BaseHandler):
    """
    APP审核开关：/core/appversion/isopen
    """
    ios_version = [
        "1.0.1",
    ]

    android_version = [
        'baidu2.0.1',
    ]

    @filter_params(get=rule)
    def get(self, params):

        result = {
            'all_open': 1,
            'reward_open': 1,               # 打赏功能
            'wechat_open': 1,               # 买卖微信功能
            'private_img_open': 1,          # 私密照片功能
            'private_video_open': 1,        # 私密视频功能
        }

        if params["version"] in self.ios_version:
            result["all_open"] = 0
        elif params["version"] in self.android_version:
            result["all_open"] = 0
        return json_success_response(result)

    def post(self):
        return json_fail_response(501)


class VersionHandler(BaseHandler):
    """
    获取版本更新信息: /core/appversion/getversion
    """

    @filter_params(get=rule)
    def get(self, params):

        result = {
            "data": 0,
            "force": 0
        }

        version = int(params["version"].replace(".", "")) * 10

        new_app = AppVersionModel.query_last_app_version_by_device_type(device_type=params["device_type"])
        if new_app is not None:
            # 去除数据库中的数据
            result = dict(result, **(new_app.to_dict(filter_params=True)))

            # 通知APP有新版本
            if new_app.version2long > version:
                result["data"] = 1
                # 是否启动强制更新
                result["force"] = 0

        # 是否杀死当前app，并跳转到新app
        result["kill"] = 0
        # 新app的下载地址
        result["app_url"] = ""

        return json_success_response(result)

    def post(self):
        return json_fail_response(501)


core.add_url_rule("/appversion/isopen", view_func=OpenHandler.as_view("isopen"))
core.add_url_rule("/appversion/getversion", view_func=VersionHandler.as_view("version"))
