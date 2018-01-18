"""
开发环境的配置文件类

配置内容项目:
1. MySql
2. Redis
3. Memcached
4. Mongodb
"""
import configparser
import os

from config.base.base_config import BaseConfig

basedir = os.path.abspath(os.path.dirname(__file__))

INI_MYSQL = configparser.ConfigParser()
INI_MYSQL.read(os.path.join(basedir, 'mysql.ini'))

INI_MEMCACHED = configparser.ConfigParser()
INI_MEMCACHED.read(os.path.join(basedir, 'memcached.ini'))


class DevelopConfig(BaseConfig):
    # Open Debug mode
    DEBUG = True

    @staticmethod
    def init_app(app):
        # 配置SQLAlchemy
        DevelopConfig.config_sqlalchemy(app)

    @staticmethod
    def config_sqlalchemy(app):
        """
        SQLAlchemy 多数据库绑定
        """
        sql_binds = dict()

        # 读取mysql.ini中的内容进行绑定
        for section in INI_MYSQL.sections():
            user_name = INI_MYSQL[section]["master.username"]
            password = INI_MYSQL[section]["master.password"]
            host = INI_MYSQL[section]["master.host"]
            port = INI_MYSQL[section]["master.port"]

            # 拼接连接mysql的URI
            sql_binds[section] = "mysql://%s:%s@%s:%s/%s" % (user_name, password, host, port, section)

        # 添加到配置文件中
        app.config["SQLALCHEMY_BINDS"] = sql_binds
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    @staticmethod
    def config_memcached(app):
        """
        Memcached服务器集群注册
        """
        memcached = []
        for section in INI_MEMCACHED.sections():
            server = INI_MEMCACHED[section]["host"] + ":" + INI_MEMCACHED[section]["port"]
            if server:
                memcached.append(server)
        app.config["CACHE_MEMCACHED_SERVERS"] = memcached
