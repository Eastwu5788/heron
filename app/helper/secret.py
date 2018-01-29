import hashlib
import time


def md5(string):
    """
    生成一个字符串的md5值
    :param string:
    :return:
    """
    md5_obj = hashlib.md5()
    md5_obj.update(string.encode("utf8"))
    return md5_obj.hexdigest()


def get_seed(string='', length=32):
    """
    获取特定长度的随机字符串
    热点：任意两次的字符串不相同
    """
    from config.setting import SECRET_KEY

    string += str(time.time())
    string += SECRET_KEY
    sha512 = hashlib.sha512()
    sha512.update(bytes(string, encoding="utf-8"))
    string = sha512.hexdigest()
    return string[:length]


def generate_request_sign(params, salt=""):
    """
    服务器端生成请求的签名参数
    :return: 签名后的字符串
    """
    # 按照请求参数字典key的升序排列
    order_arr = sorted(params, key=lambda obj: obj[0], reverse=False)

    # 拼接成字符串
    result_str = ''
    for item_tup in order_arr:
        result_str += item_tup[0] + '=' + item_tup[1] + ':'
    # 追加salt
    result_str += "salt=" + salt

    # 生成签名值
    return md5(result_str)


def generate_password(user_id=0, password=""):

    from config.setting import SECRET_KEY

    string = SECRET_KEY + password + str(user_id)
    sha512 = hashlib.sha512()
    sha512.update(bytes(string, encoding="utf-8"))
    new_password = sha512.hexdigest()
    return new_password[:64]


def check_password(user_id=0, password="", pwd=""):
    user_pwd = generate_password(user_id, password)
    return user_pwd == pwd
