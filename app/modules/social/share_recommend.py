from flask import g
from . import social

from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.share import ShareModel
from app.models.social.share_recommend import ShareRecommendModel
from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "position": Rule(direct_type=int, allow_empty=True, default=0),
        "share_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):
        # 查询到被推荐动态的id
        share_id_list = ShareRecommendModel.query_share_recommend_id_list(params["position"], g.account["user_id"], params["share_id"])
        # 根据动态id查询动态详细信息
        share_list = ShareModel.query_share_info_list(share_id_list)
        # 格式化动态
        result = ShareModel.format_share_model(share_list, account=0)
        # 返回结果
        return json_success_response(result)


social.add_url_rule("/getsharerecommend/index", view_func=IndexHandler.as_view("share_recommend_index"))
