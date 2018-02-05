from flask import g
from . import social
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.base.redis import RedisModel
from app.models.social.comment_relation import CommentRelationModel
from app.models.account.user_info import UserInfoModel
from app.models.social.comment import CommentModel
from app.models.social.share import ShareModel, status_public
from app.models.social.image import ImageModel

from app.helper.response import *
from app.helper.auth import login_required
from app.helper.utils import array_column, array_column_key


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


class GetCommentHandler(BaseHandler):

    rule = {
        "last_id": Rule(direct_type=int)
    }

    @login_required
    def get(self, params):
        RedisModel.reset_new_message(g.account["user_id"], RedisModel.new_comment)

        comment_list = CommentRelationModel.query_relation_info(g.account["user_id"], 20, params["last_id"])
        if not comment_list:
            return json_success_response(list())

        comment_id_list = array_column(comment_list, "comment_id")
        comment_info_list = CommentModel.query_comment_list(comment_id_list)
        comment_info_dict = array_column_key(comment_info_list, "comment_id")
        if not comment_info_list:
            return json_success_response(list())

        result = list()
        for comment_relation_model in comment_list:
            pass

    @staticmethod
    def query_share_info(share_id):
        share_info = ShareModel.query_share_model(share_id)
        if not share_info or share_info.status not in status_public:
            return None

        user_info = UserInfoModel.query_user_model_by_id(share_info.user_id)
        if share_info.type_id == 10:
            image = ImageModel.query.filter_by(share_id=share_id, status=1).order_by(ImageModel.image_id.asc()).first()
            pass




social.add_url_rule("/chat/isnewcomment", view_func=NewCommentHandler.as_view("chat_is_new_comment"))