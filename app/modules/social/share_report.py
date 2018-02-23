from flask import g
from app import db
from . import social
from app.modules.base.base_handler import BaseHandler

from app.models.social.share_report import ShareReportModel
from app.models.social.share_meta import ShareMetaModel

from app.helper.auth import login_required
from app.modules.vendor.pre_request import Rule, filter_params, Length
from app.helper.response import *


class IndexHandler(BaseHandler):

    rule = {
        "report_name_id": Rule(direct_type=int),
        "reason": Rule(),
        "other_reason": Rule(allow_empty=True, default="", length=Length(min_len=0, max_len=100)),
        "type": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        share_report = ShareReportModel.query_share_report(g.account["user_id"], params["report_name_id"], params["type"])
        if share_report:
            return json_fail_response(2124)

        share_report = ShareReportModel()
        share_report.user_id = g.account["user_id"]
        share_report.report_name_id = params["report_name_id"]
        share_report.reason = params["reason"]
        share_report.other_reason = params["other_reason"]
        share_report.type = params["type"]

        db.session.add(share_report)

        if share_report.type == 2:
            ShareMetaModel.update_share_meta_model(params["report_name_id"], params=["report"])

        db.session.commit()
        return json_success_response({"data": 1, "message": "操作成功"})


social.add_url_rule("/addsharereport/index", view_func=IndexHandler.as_view("add_share_repost_index"))
