from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache

from config.setting import config, MIDDLEWARE
from .middleware.base_middleware import BaseMiddleWare

db = SQLAlchemy()
cache = Cache()


def create_app(config_name):
    """
    创建并根据配置文件初始化一个Flask App
    :param config_name: 配置文件的名称（pro）
    :return:
    """
    # init a flask app
    app = Flask(__name__)

    # 加载配置类的静态配置
    app.config.from_object(config[config_name])
    # 调用配置类的init_app()函数，执行动态配置
    config[config_name].init_app(app)

    # 初始化SQLAlchemy数据库
    db.init_app(app)
    cache.init_app(app)

    # 注册蓝图 TODO: 蓝图写到ini配置文件中
    from app.modules.build import build
    app.register_blueprint(build, url_prefix="/build")

    from app.modules.core import core
    app.register_blueprint(core, url_prefix="/core")

    from app.modules.passport import passport
    app.register_blueprint(passport, url_prefix="/passport")

    # 注册中间件
    for middle in MIDDLEWARE:
        if issubclass(middle, BaseMiddleWare):
            app.before_request(middle.before_request)
            app.after_request(middle.after_request)

    return app


