from . import social
from app.modules.base.base_handler import BaseHandler

from app.models.social.share import ShareModel

from app.helper.response import *


class IndexHandler(BaseHandler):

    def get(self):
        share_list = ShareModel.query_share_info_list([1, 2])
        result = ShareModel.format_share_model(share_list, account=0)
        return json_success_response(result)


social.add_url_rule("/sharerecommend/index", view_func=IndexHandler.as_view("share_recommend_index"))
