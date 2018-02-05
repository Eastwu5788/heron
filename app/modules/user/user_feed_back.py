import json
from flask import g
from . import user
from app import db
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.core.user_feedback import UserFeedBackModel


from app.helper.upload import UploadImage
from app.helper.auth import login_required
from app.helper.response import *


class AddHandler(BaseHandler):

    max_upload_image_count = 6

    rule = {
        "content": Rule(),
        "system": Rule(),
        "version": Rule(),
        "type": Rule(direct_type=int, allow_empty=True, default=0),
        "mobile_model": Rule(),
        "user_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        img_uploader = UploadImage()
        img_id_list = list()
        if img_uploader.images:
            if len(img_uploader.images) > AddHandler.max_upload_image_count:
                return json_fail_response(2407)

            img_uploader.save_images()
            for image_info in img_uploader.images:
                img_model = image_info["image"]
                img_model.user_id = g.account["user_id"]
                img_model.type = 13
                img_id_list.append(img_model.image_id)
            db.session.commit()

        json_data = {"image_id": img_id_list}
        if params["type"] == 1:
            json_data["user_id"] = params["user_id"]

        user_feed_back = UserFeedBackModel()
        user_feed_back.user_id = g.account["user_id"]
        user_feed_back.type = params["type"]
        user_feed_back.content = params["content"]
        user_feed_back.system = params["system"]
        user_feed_back.version = params["version"]
        user_feed_back.mobile_model = params["mobile_model"]
        user_feed_back.json_data = json.dumps(json_data)

        db.session.add(user_feed_back)

        result = {
            "data": 1,
            "message": "感谢您的反馈"
        }

        if params["type"] == 1:
            result["message"] = "投诉成功，我们会尽快处理！"

        try:
            db.session.commit()
        except:
            result["data"] = 0
            if params["type"] == 1:
                result["message"] = "投诉失败，请稍后重试！"
            else:
                result["message"] = "留言未受理"

        return json_success_response(result)


user.add_url_rule("/userfeedback/add", view_func=AddHandler.as_view("user_feed_back_add"))

