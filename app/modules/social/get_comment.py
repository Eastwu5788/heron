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

from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0),
    }

    @filter_params(get=rule)
    def get(self, params):
        result = CommentModel.query_share_comment_list(params["share_id"], g.account["user_id"], params["last_id"])
        return json_success_response(result)


social.add_url_rule("/getcomment/index", view_func=IndexHandler.as_view("get_comment_index"))
