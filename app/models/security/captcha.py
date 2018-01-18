import random
from app import cache
from config.setting import MOBILE_WHITE_LIST


class CaptchaModel(object):

    sms_cache_key = "token:%s:chanel:%s:country:%s:type:%d"

    cache_key = ""

    @staticmethod
    def send_china_sms_code(mobile="", sms_type=1):
        # 参数错误
        if not mobile or not CaptchaModel.cache_key:
            return False

        # 白名单中的手机号不发送验证码
        if mobile in MOBILE_WHITE_LIST:
            return True

        # 参数准备
        cache_time = 60*60*10
        sms_code = random.randint(1000, 9999)

        # 发送验证码
        send_result = True

        if send_result:
            cache.set(CaptchaModel.cache_key, sms_code, cache_time)
            return True
        else:
            # TODO: 统计发送失败记录
            pass

        return False

    @staticmethod
    def send_abroad_sms_code(mobile="", sms_type=1, country=1):
        return False
