from . import user
from app import db
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.follow import FollowModel
from app.models.base.redis import RedisModel
from app.models.social.social_meta import SocialMetaModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import *
from app.helper.auth import login_required


class IndexHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int),
        "follow_id": Rule(direct_type=int),
        "status": Rule(direct_type=int, enum=(0, 1))
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        # 处理自己关注自己的情况
        if params["user_id"] == params["follow_id"]:
            return json_fail_response(2301)

        user_follow = FollowModel.query_user_follow(user_id=params["user_id"], follow_id=params["follow_id"])

        result = dict()
        if not user_follow:
            user_follow = FollowModel()
            user_follow.user_id = params["user_id"]
            user_follow.follow_id = params["follow_id"]
            user_follow.status = params["status"]

            db.session.add(user_follow)
            db.session.commit()

            # 添加新的关注的redis
            if params["status"] == 1:
                RedisModel.add_new_message(params["follow_id"], RedisModel.new_follow)

            result = {
                "data": 1,
                "message": "关注成功" if params["status"] == 1 else "取消成功"
            }

            IndexHandler.update_social_meta(params["user_id"], params["follow_id"], params["status"])

        elif user_follow.status != params["status"]:
            user_follow.status = params["status"]

            db.session.commit()
            # 添加新的关注的redis
            if params["status"] == 1:
                RedisModel.add_new_message(params["follow_id"], RedisModel.new_follow)

            result = {
                "data": 1,
                "message": "关注成功" if params["status"] == 1 else "取消成功"
            }
            IndexHandler.update_social_meta(params["user_id"], params["follow_id"], params["status"])

        elif user_follow.status == 1:
            result = {
                "data": 1,
                "message": "已关注",
            }

        follow_status = FollowModel.query_relation_to_user_list(params["user_id"], [params["follow_id"]])
        result["follow_status"] = follow_status[params["follow_id"]]

        UserInfoModel.query_user_model_by_id(params["user_id"], True)
        UserInfoModel.query_user_model_by_id(params["follow_id"], True)
        return json_success_response(result)

    @staticmethod
    def update_social_meta(user_id, follow_id, status):
        SocialMetaModel.update_social_meta_model(user_id, ["following"], status == 1)
        SocialMetaModel.update_social_meta_model(follow_id, ["follower"], status == 1)


user.add_url_rule("/addfollow/index", view_func=IndexHandler.as_view("add_follow_index"))
