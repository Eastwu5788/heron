import random
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

from app import cache
from config.setting import MOBILE_WHITE_LIST
from heron import app

# 云片客户端
client = YunpianClient(app.config["SMS_YP_API_KEY"])


class CaptchaModel(object):

    sms_cache_key = "token:%s:chanel:%s:country:%s:type:%d"

    cache_key = ""

    @staticmethod
    def verify_sms_code(sms_code):
        """
        验证短信验证码
        :param sms_code: 用户输入的短信验证码
        :return: 验证结果
        """
        cache_code = cache.get(CaptchaModel.cache_key)
        if not cache_code or cache_code != sms_code:
            return False
        return True

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

        params = {YC.MOBILE: mobile, YC.TEXT: CaptchaModel.generate_sms_content(sms_code, 1)}
        # 发送验证码
        send_result = client.sms().single_send(params)

        if send_result.code() == 0:
            cache.set(CaptchaModel.cache_key, sms_code, cache_time)
            return True
        else:
            # TODO: 统计发送失败记录
            pass

        return False

    @staticmethod
    def send_abroad_sms_code(mobile="", sms_type=1, country=1):
        return False

    @staticmethod
    def generate_sms_content(code=0, template_type=0):
        """
        根据短信类型，生成短信内容
        :param code: 短信验证码（可能不需要）
        :param template_type: 短信模板类型
        :return:
        """
        sms_content = ""
        if template_type == 0:
            sms_content = '【啊哈APP】您的验证码是' + str(code) + '。如非本人操作，请忽略本短信'
        elif template_type == 1:
            sms_content = '【啊哈APP】爸爸，您的验证码是' + str(code) + '。快来玩我！'
        return sms_content
