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

INI_CONFIG = configparser.ConfigParser()
INI_CONFIG.read(os.path.join(basedir, "config.ini"))

INI_REDIS = configparser.ConfigParser()
INI_REDIS.read(os.path.join(basedir, "redis.ini"))


class DevelopConfig(BaseConfig):
    # Open Debug mode
    DEBUG = True

    LOGGER_NAME = "hero_flask_log"

    # Redis 配置（TODO: 集群）
    CACHE_REDIS_HOST = INI_REDIS["redis"]["host"]
    CACHE_REDIS_PORT = INI_REDIS["redis"]["port"]

    # 短信平台云片的API KEY
    SMS_YP_API_KEY = INI_CONFIG["sms_yp"]["api_key"]

    # 图片上传路径和URI
    UPLOAD_IMG_PATH = INI_CONFIG["upload_image"]["image_upload_path"]
    IMAGE_HOST = INI_CONFIG["upload_image"]["image_uri"]

    # 视频上传路径和URI
    UPLOAD_VIDEO_PATH = INI_CONFIG["upload_video"]["video_upload_path"]
    VIDEO_HOST = INI_CONFIG["upload_video"]["video_uri"]

    # 音频上传路径和URI
    UPLOAD_AUDIO_PATH = INI_CONFIG["upload_audio"]["audio_upload_path"]
    AUDIO_HOST = INI_CONFIG["upload_audio"]["audio_uri"]

    # 微信支付相关账号
    WX_APP_ID = INI_CONFIG["weixin"]["appid"]
    WX_MCH_ID = INI_CONFIG["weixin"]["mch_id"]
    WX_MCH_KEY = INI_CONFIG["weixin"]["partner_key"]

    # 支付宝支付相关账号
    ALI_APP_ID = INI_CONFIG["ali"]["appid"]
    ALI_PARTNER_ID = INI_CONFIG["ali"]["partner_id"]
    ALI_SELLER_ID = INI_CONFIG["ali"]["seller_id"]
    ALI_KEY = INI_CONFIG["ali"]["key"]
    ALI_SIGN_TYPE = INI_CONFIG["ali"]["sign_type"]
    ALI_PRIVATE_KEY_PATH = INI_CONFIG["ali"]["private_key_path"]
    ALI_PUBLIC_KEY_PATH = INI_CONFIG["ali"]["public_key_path"]
    ALI_CACERT_PATH = INI_CONFIG["ali"]["cacert"]

    @staticmethod
    def init_app(app):
        # 配置SQLAlchemy
        DevelopConfig.config_sqlalchemy(app)
        # 配置Memcached服务器
        DevelopConfig.config_memcached(app)

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

