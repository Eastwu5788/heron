# -*- coding: utf-8 -*-
# (C) Wu Dong, 2018
# All rights reserved
__author__ = 'Wu Dong <wudong@eastwu.cn>'
__time__ = '2018/4/27 下午2:30'
"""
Usage:

# 单参数情况
@cache('Test:User:dev:%s' % '{user_id}')
def query_result(user_id, pid=13):
    return user_id, pid

# 多参数情况
@cache('Test:User:dev:%s:%s' % ('{user_id}', '{pid}'))
def query_result(user_id, pid=14):
    return user_id, pid

# 按参数顺序拼接key
@cache('Text:User:dev:%s:%s')
def query_result(user_id, pid=15):
    return user_id, pid

# 指定参数的数据类型
@cache('Test:User:%(user_id)d:%(pid)d')
def query_result(user_id, pid=15):
    return user_id, pid

# 使用不同的redis库，或者memcache
@cache('Test:User:%(user_id)d:%(pid)d', mc=CACHE[14])
def query_result2(user_id, pid=15):
    return user_id, pid
    
# 指定过期时间
@cache('Test:User:%(user_id)d:%(pid)d', expire=3600)
def query_result2(user_id, pid=15):
    return user_id, pid

# 指定refresh进行刷新
print(query_result(user_id=111111, refresh=True))

"""
import inspect
import re
from functools import wraps
from src.leleProxy.config import CACHE


# 默认数据永不过期
MC_DEFAULT_EXPIRE_IN = 0

__formaters = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')


def formater(text):
    """
    生成格式化的具体参数
    :param text: 匹配的字符串
    """
    percent = percent_pattern.findall(text)
    brace = brace_pattern.search(text)
    if percent and brace:
        raise Exception('mixed format is not allowed')

    # 处理 xxx:xxx:%s:%s 的情况
    if percent:
        n = len(percent)
        return lambda *args, **kwargs: text % tuple(args[:n])

    # 处理xxx:xxx:%(p1)d:%(p2)d 的情况
    elif "%(" in text:
        return lambda *args, **kwargs: text % kwargs

    # 处理 xxx:xxx:{p1}:{p2} 的情况
    else:
        return text.format


def format(text, *args, **kwargs):
    """
    格式化字符串
    :param text: 原始字符串
    :param args:
    :param kwargs:
    :return:
    """
    f = __formaters.get(text)
    if f is None:
        f = formater(text)
        __formaters[text] = f
    return f(*args, **kwargs)


def gen_key_factory(key_pattern, arg_names, defaults):
    # 将函数的参数和默认值拼接成字典，由于开头的参数有可能没有默认值，所有需要从后往前拼
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}

    # 检查表达式是否可以调用
    if callable(key_pattern):
        names = inspect.getargspec(key_pattern)[0]

    def gen_key(*params, **kwargs):
        copy_args = args.copy()

        # 更新用户输入的实际参数
        copy_args.update(zip(arg_names, params))
        copy_args.update(kwargs)

        # 将表达式格式化成字符串
        if callable(key_pattern):
            key = key_pattern(*[copy_args[n] for n in names])
        else:
            key = format(key_pattern, *[copy_args[n] for n in arg_names], **copy_args)
        return key and key.replace(' ', '_'), copy_args

    return gen_key


def cache(key_pattern, mc=CACHE[13], expire=MC_DEFAULT_EXPIRE_IN):
    """
    缓存使用的装饰器
    """
    def deco(func):
        # 解析函数的所参数
        arg_names, varargs, varkw, defaults = inspect.getargspec(func)
        # 不支持包含*args或者**kwargs参数的函数
        if varargs or varkw:
            raise Exception("do not support varargs")

        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(func)
        def _(*params, **kwargs):
            key, args = gen_key(*params, **kwargs)
            if not key:
                return func(*params, **kwargs)

            # 判断是否需要进行刷新
            refresh = kwargs.pop('refresh', False)
            result = mc.get(key) if not refresh else None

            # 缓存没有数据时，调用函数获取数据并刷新缓存
            if result is None:
                result = func(*params, **kwargs)
                if result is not None:
                    mc.set(key, result, expire)

            return result

        _.original_function = func
        return _

    return deco

