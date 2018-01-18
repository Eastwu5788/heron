"""
配置文件基类
所有的配置文件类，从此类继承
"""


class BaseConfig(object):

    # 缓存类型
    CACHE_TYPE = "memcached"
    # 缓存Key的前缀
    CACHE_KEY_PREFIX = "Heron:"

    @staticmethod
    def init_app(app):
        pass

