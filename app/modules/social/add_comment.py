from flask import g
from . import social
from app import db
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.account.user_info import UserInfoModel
from app.models.social.share import ShareModel
from app.models.social.comment import CommentModel
from app.models.social.share_meta import ShareMetaModel
from app.models.base.redis import RedisModel
from app.models.social.comment_relation import CommentRelationModel

from app.helper.response import *
from app.helper.auth import login_required


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
        "user_id": Rule(direct_type=int),
        "reply_comment_id": Rule(direct_type=int, allow_empty=True, default=0),
        "content": Rule(),
        "type": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        share_info = ShareModel.query_share_model(params["share_id"])
        if not share_info:
            return json_fail_response(2405)

        comment_model = None

        # 回复某一条评论
        if params["reply_comment_id"]:
            comment_model = CommentModel.query_comment_by_id(params["reply_comment_id"])
            if not comment_model:
                return json_fail_response(2406)

            if comment_model.layer_comment_id:
                layer_comment_model = CommentModel.query_comment_by_id(comment_model.layer_comment_id)
                if not layer_comment_model:
                    return json_fail_response(2406)

        comment = CommentModel()
        comment.share_id = params["share_id"]
        comment.user_id = g.account["user_id"]
        comment.reply_comment_id = params["reply_comment_id"]
        comment.content = params["content"]
        comment.type = params["type"]
        comment.status = 1

        if params["reply_comment_id"]:
            if not comment_model.layer_comment_id:
                comment.layer_comment_id = comment_model.comment_id
            else:
                comment.layer_comment_id = comment_model.layer_comment_id
            if comment_model.type == 1:
                comment.type = 1

        db.session.add(comment)
        db.session.commit()

        ShareMetaModel.update_share_meta_model(params["share_id"], share_info.user_id, ["comment"])

        result = comment.to_dict()
        user = UserInfoModel.query_user_model_by_id(g.account["user_id"])
        result["user_info"] = UserInfoModel.format_user_info(user)
        if comment.reply_comment_id:
            reply_user_info = UserInfoModel.query_user_model_by_id(comment_model.user_id)
            result["reply_user_info"] = UserInfoModel.format_user_info(reply_user_info)

            # 回复的动态的所有者不是自己
            if comment_model.user_id != g.account["user_id"]:
                CommentRelationModel(g.account["user_id"], comment_model.user_id, share_info.share_id,
                                     comment.comment_id, comment_model.comment_id)
                RedisModel.add_new_message(comment_model.user_id, RedisModel.new_comment)

        # 动态的主人不是自己
        if share_info.user_id != g.account["user_id"]:
            if comment_model and comment_model.user_id == share_info.user_id:
                pass
            else:
                CommentRelationModel(g.account["user_id"], share_info.user_id, share_info.share_id,
                                     comment.comment_id, params["reply_comment_id"])
                RedisModel.add_new_message(share_info.user_id, RedisModel.new_comment)

        share_meta = ShareMetaModel.query_share_meta_model(params["share_id"])
        result["comment_count"] = share_meta.comment if share_meta else 0

        # 回复的数据结构
        if params["reply_comment_id"]:
            result = {
                "comment_id": comment.comment_id,
                "share_id": comment.share_id,
                "user_id": comment.user_id,
                "reply_comment_id": comment.reply_comment_id,
                "content": comment.content,
                "type": comment.type,
                "status": comment.status,
                "created_time": comment.created_time,
                "nickname": user.nickname,
                "reply_nickname": reply_user_info.nickname,
            }

        return json_success_response(result)


social.add_url_rule("/addcomment/index", view_func=IndexHandler.as_view("add_comment_index"))
