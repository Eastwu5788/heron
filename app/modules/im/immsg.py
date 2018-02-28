import json
from flask import g
from . import im
from app.modules.base.base_handler import BaseHandler
from app.models.account.user_id_relation import UserIdRelationModel
from app.models.im.im_msg import IMMsgModel
from app.modules.vendor.pre_request import filter_params, Rule
from app.helper.auth import login_required
from app.helper.response import json_success_response


class CreateHandler(BaseHandler):

    rule = {
        "to_uid": Rule(),
        "content": Rule(),
        "msg_type": Rule(direct_type=int),
        "type": Rule(direct_type=int),
        "pub_time": Rule(),
        "image": Rule(direct_type=int, allow_empty=True, default=0),
        "video": Rule(direct_type=int, allow_empty=True, default=0),
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        # 查询用户uid
        user_id_relation_model = UserIdRelationModel.query_user_by_ease_mob_id(params["to_uid"])
        params["to_uid"] = user_id_relation_model.user_id if user_id_relation_model else params["to_uid"]

        params["chatfrom"] = g.account["user_id"]
        params["chatto"] = params["to_uid"]
        params["type"] = 1

        if params["msg_type"] == 2:
            json_data = {"image": params["image"]}
        elif params["msg_type"] == 3:
            json_data = {"audio": params["audio"]}
        elif params["msg_type"] == 4:
            json_data = {"video": params["video"]}
        else:
            json_data = {}
        if json_data:
            params["json_data"] = json.dump(json_data)

        im_model = IMMsgModel(params=params)
        return json_success_response(im_model.to_dict())


im.add_url_rule("/immsg/create", view_func=CreateHandler.as_view("immsg_create"))
