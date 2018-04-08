# -*- coding: utf-8 -*-
# (C) Wu Dong, 2018
# All rights reserved
__author__ = 'Wu Dong <wudong@eastwu.cn>'

"""
Usage:

开发者模式运行: python heron.py dev

生产环境运行: python heron.py pro -p 4389 -h 0.0.0.0 -t 3
参数说明: 
-p：指定端口号
-h：指定主机ip
-t：开启的进程数量
"""

from app import create_app
from flask_script import Manager

app = create_app('dev')
manager = Manager(app)


@manager.command
def dev():
    app.run()


@manager.option('-p', '--port', help='Server run port', default=8640)
@manager.option('-h', '--host', help='Server run host', default='0.0.0.0')
@manager.option('-t', '--thread', help='Thread count', default=3)
def pro(host, port, thread):
    app.run(host=host, port=int(port), processes=int(thread))


if __name__ == '__main__':
    manager.run()
