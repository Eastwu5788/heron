"""
生产环境的配置文件

配置内容：
1. MySQL
2. Redis
3. Memcached
4. Other
"""
from config.base.base_config import BaseConfig


class ProductConfig(BaseConfig):

    @staticmethod
    def init_app(app):
        pass
