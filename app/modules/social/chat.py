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
from app.models.commerce.order_meta import OrderMetaModel

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
    @filter_params(get=rule)
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
            share_info = GetCommentHandler.query_share_info(comment_relation_model.share_id)
            if not share_info:
                continue

            if comment_info_dict[comment_relation_model.comment_id].user_id == g.account["user_id"]:
                continue

            user_info = UserInfoModel.query_user_model_by_id(comment_relation_model.user_id)

            item = dict()
            item["share_id"] = comment_relation_model.share_id
            item["share_img"] = share_info["image"]
            item["share_content"] = share_info["content"]
            item["share_nickname"] = share_info["nickname"]
            item["content"] = comment_info_dict[comment_relation_model.comment_id].content
            item["created_time"] = comment_relation_model.created_time
            item["status"] = comment_relation_model.status
            item["comment_id"] = comment_relation_model.comment_id
            item["user_info"] = UserInfoModel.format_user_info(user_info)
            result.append(item)

        return json_success_response(result)

    @staticmethod
    def query_share_info(share_id):
        share_info = ShareModel.query_share_model(share_id)
        if not share_info or share_info.status not in status_public:
            return None

        user_info = UserInfoModel.query_user_model_by_id(share_info.user_id)
        if share_info.type_id == 10:
            image = ImageModel.query.filter_by(share_id=share_id, status=1).order_by(ImageModel.image_id.asc()).first()
            image_url = ImageModel.generate_image_url(image, 'c')
        elif share_info.type_id == 11:
            image = ImageModel.query.filter_by(share_id=share_id, status=1).order_by(ImageModel.image_id.asc()).first()
            image_url = ImageModel.generate_image_url(image, 'x')
        elif share_info.type_id == 30:
            image_url = ""
        else:
            image_url = UserInfoModel.format_user_info(user_info)["avatar"]

        result = {
            "image": image_url,
            "content": share_info.content,
            "nickname": user_info.nickname,
        }
        return result


class TradeHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        from collections import OrderedDict
        query_params = OrderedDict()
        query_params["pay_status"] = 1
        query_params["seller_id"] = params["user_id"]
        query_params["buyer_id"] = g.account["user_id"]

        order_meta = OrderMetaModel.query_order_meta(query_params)

        result = {
            "data": 1 if order_meta else 0,
            "message": "已有消费" if order_meta else "尚未消费"
        }
        return json_success_response(result)


social.add_url_rule("/chat/isnewcomment", view_func=NewCommentHandler.as_view("chat_is_new_comment"))
social.add_url_rule("/chat/getcomment", view_func=GetCommentHandler.as_view("chat_get_comment"))
social.add_url_rule("/chat/tradeforother", view_func=TradeHandler.as_view("trade_for_other"))
