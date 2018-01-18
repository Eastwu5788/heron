import json
import time

from app.common.error_message import error_message
from .json_encoder import JsonEncoder


def json_response(code=0, body=None, message=""):
    """
    通用JSON响应方法
    :param code: 响应识别码
    :param body: 响应内容主体
    :param message: 错误提示
    :return: JSON
    """
    result = {
        "code": code,
        "message": message,
        "result": body,
        "timestamp": int(time.time())
    }
    return json.dumps(result, cls=JsonEncoder)


def json_success_response(body={}):
    """
    响应内容正确
    :param body: 响应体
    """
    return json_response(body=body, message="请求成功")


def json_fail_response(code=500, message=""):
    """
    请求出错的响应
    :param code: 响应错误识别码
    :param message: 错误友好提示内容
    """
    if message:
        pass
    else:
        message = error_message[code]
        if not message:
            message = "服务器内部错误"

    return json_response(code, body={}, message=message)
