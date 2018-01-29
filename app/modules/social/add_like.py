from flask import g
from . import social
from app import db
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.share import ShareModel
from app.models.social.like import LikeModel
from app.models.account.user_info import UserInfoModel
from app.models.social.share_meta import ShareMetaModel

from app.helper.auth import login_required
from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
        "status": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):

        share_model = ShareModel.query_share_model(params["share_id"])
        if not share_model:
            return json_fail_response(2405)

        like_model = LikeModel.query_like_model(g.account["user_id"], params["share_id"])
        user_info = UserInfoModel.query_user_model_by_id(g.account["user_id"])
        if not like_model:

            if params["status"] != 1:
                result = {
                    "data": 0,
                    "message": "操作失败",
                }
                return json_success_response(result)

            like_model = LikeModel()
            like_model.share_id = params["share_id"]
            like_model.user_id = g.account["user_id"]
            like_model.status = 1
            db.session.add(like_model)
            db.session.commit()

            result = {
                "data": 1,
                "status": params["status"],
                "user_info": UserInfoModel.format_user_info(user_info),
                "message": "点赞成功",
            }
            ShareMetaModel.update_share_meta_model(share_model.share_id, share_model.user_id, ["like"])
        elif like_model.status != params["status"]:
            like_model.status = params["status"]
            db.session.commit()

            result = {
                "data": 1,
                "status": params["status"],
                "user_info": UserInfoModel.format_user_info(user_info),
                "message": "点赞成功" if params["status"] == 1 else "取消点赞成功",
            }
            ShareMetaModel.update_share_meta_model(share_model.share_id, share_model.user_id, ["like"], params["status"] == 1)
        else:
            if params["status"] == 1:
                result = {
                    "data": 0,
                    "status": params["status"],
                    "user_info": UserInfoModel.format_user_info(user_info),
                    "message": "已点赞",
                }
            else:
                result = {
                    "data": 0,
                    "status": params["status"],
                    "user_info": UserInfoModel.format_user_info(user_info),
                    "message": "未点赞",
                }

        share_meta = ShareMetaModel.query.filter_by(share_id=share_model.share_id).first()
        result["like_count"] = share_meta.like
        return json_success_response(result)


social.add_url_rule("/addlike/index", view_func=IndexHandler.as_view("add_like_index"))
