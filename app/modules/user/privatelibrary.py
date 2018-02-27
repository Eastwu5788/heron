import random

from flask import g
from . import user
from app import redis, db
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.image import ImageModel
from app.models.base.redis import RedisModel
from app.models.account.user_wechat import UserWeChatModel

from app.helper.auth import login_required
from app.helper.utils import array_column
from app.helper.response import json_success_response, json_fail_response
from app.helper.upload import UploadImage
from app.helper.upload import UploadVideo


private_library_cache_key = "PrivateLibraryHandler:Cache:Type:"


class PrivateLibraryHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int),
        "type": Rule(direct_type=int, enum=[11, 31]),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0),
        "offset": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        result = {
            "offset": 0,
            "want_buy": 0,
            "result_data": list()
        }

        # 私密照片
        if params["type"] == 11:
            # 自己看自己的私密照片
            if params["user_id"] == g.account["user_id"]:
                result["result_data"] = ImageModel.query_private_image(params["user_id"],
                                                                       g.account["user_id"],
                                                                       params["last_id"])
            # 查看别人的私密照片
            else:
                # 第一次请求，需要生成一个随机量
                if params["offset"] == 0 and params["last_id"] == 0:
                    params["offset"] = int(PrivateLibraryHandler.random_private_library_offset(params["type"], params["user_id"]))

                result["result_data"] = ImageModel.query_random_private_image(params["user_id"],
                                                                              g.account["user_id"],
                                                                              params["last_id"],
                                                                              params["offset"])

            result["want_buy"] = RedisModel.query_new_message(params["user_id"], RedisModel.private_image_want)
        # 私密视频
        else:
            pass

        return json_success_response(result)

    @staticmethod
    def random_private_library_offset(library_type, user_id, refresh=False):
        if not user_id:
            return 0

        cache_key = private_library_cache_key + str(library_type) + ":" + str(user_id)
        # 从集合中随机取一个值
        rand_id = redis.srandmember(cache_key)
        # Redis随机取值失败或者需要刷新
        if not rand_id or refresh:
            # 读取数据库数据
            if library_type == 11:
                model_list = ImageModel.query.filter_by(user_id=user_id, type=11, status=1).all()
                cache_id_list = array_column(model_list, "image_id")
            else:
                cache_id_list = []
            # 更新Redis并返回随机值
            redis.delete(cache_key)
            if cache_id_list:
                redis.sadd(cache_key, *cache_id_list)
                return random.choice(cache_id_list)
            else:
                return 1
        else:
            return rand_id


class UploadPrivateLibraryHandler(BaseHandler):

    rule = {
        "type": Rule(direct_type=int, enum=[11, 31]),
        "price": Rule(direct_type=float)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        img_uploader = UploadImage()

        result = []

        if params["type"] == 11:
            if not img_uploader.images:
                return json_fail_response(2402)

            img_uploader.save_images()

            result = UploadPrivateLibraryHandler.upload_private_images(img_uploader.images, g.account["user_id"])
            RedisModel.reset_new_message(g.account["user_id"], RedisModel.private_image_want)
        elif params["type"] == 31:
            if not img_uploader.images:
                return json_fail_response(2203)

            video_uploader = UploadVideo()
            if not video_uploader.videos:
                return json_fail_response(2410)

            img_uploader.save_images()
            video_uploader.save_videos()

            result = UploadPrivateLibraryHandler.upload_private_video(video_uploader.videos[0]["video"],
                                                                      img_uploader.images[0]["image"],
                                                                      g.account["user_id"])

            RedisModel.reset_new_message(g.account["user_id"], RedisModel.private_video_want)

        PrivateLibraryHandler.random_private_library_offset(params["type"], g.account["user_id"], True)
        return json_success_response(result)

    @staticmethod
    def upload_private_images(img_list, user_id):
        img_model_list = list()
        for img_dict in img_list:
            img_model = img_dict.get("image", None)
            if not img_model:
                continue

            img_model.user_id = user_id
            img_model.type = 11

            try:
                db.session.commit()
            except:
                continue

            img_model_list.append(img_model)

        return ImageModel.format_private_image_model(img_model_list, user_id, user_id)

    @staticmethod
    def upload_private_video(video_model, image_model, user_id):

        video_model.user_id = user_id
        video_model.type = 31
        video_model.cover_id = image_model.image_id

        video_model.screenshot_a = image_model.image_a
        video_model.screenshot_b = image_model.image_b
        video_model.screenshot_c = image_model.image_c

        image_model.user_id = user_id

        db.session.commit()

        return


class PrivateInfoHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        pri_img_model = ImageModel.query.filter_by(user_id=params["user_id"], type=11, status=1).first()
        pri_video_model = None

        result = dict()
        result["pri_image_status"] = 1 if pri_img_model else 0
        result["pri_video_status"] = 1 if pri_video_model else 0
        result["wechat_info"] = UserWeChatModel.full_wechat_info(params["user_id"], g.account["user_id"])

        return json_success_response(result)


user.add_url_rule("/privatelibrary/uploadprivatelibrary", view_func=UploadPrivateLibraryHandler.as_view("upload_private_lib"))
user.add_url_rule("/privatelibrary/privatelibrary", view_func=PrivateLibraryHandler.as_view("private_library"))
user.add_url_rule("/privatelibrary/privateinfo", view_func=PrivateInfoHandler.as_view("private_info"))
