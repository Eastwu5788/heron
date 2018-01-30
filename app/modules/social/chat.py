from flask import g
from . import social
from app.modules.base.base_handler import BaseHandler

from app.models.base.redis import RedisModel
from app.models.social.comment_relation import CommentRelationModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import *
from app.helper.auth import login_required


class NewCommentHandler(BaseHandler):

    @login_required
    def get(self):
        result = {
            "new_comment": 0,
            "image_url": ""
        }

        new_comment = RedisModel.query_new_message(g.account["user_id"], RedisModel.new_comment)
        result["new_comment"] = new_comment

        if new_comment:
            relation_list = CommentRelationModel.query_relation_info(g.account["user_id"], per_page=3, last_cid=0)
            for model in relation_list:
                if model.user_id != g.account["user_id"]:
                    user_info = UserInfoModel.query_user_model_by_id(model.user_id)
                    result["image_url"] = UserInfoModel.format_user_info(user_info)["avatar"]
                    break

        return json_success_response(result)


social.add_url_rule("/chat/isnewcomment", view_func=NewCommentHandler.as_view("chat_is_new_comment"))