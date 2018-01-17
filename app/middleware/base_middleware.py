"""
项目请求中间件基类

所有的中间件必须继承此类

请求处理之前调用before_request()函数
请求处理之后调用after_request()函数
"""


class BaseMiddleWare(object):

    @staticmethod
    def before_request():
        """
        请求之前的处理
        """
        pass

    @staticmethod
    def after_request(response):
        """
        请求结束的处理
        """
        return response

    @staticmethod
    def teardown_request(exception):
        pass
