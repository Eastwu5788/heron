from flask import g
from . import common
from app import db
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.filter_rules import Rule
from app.modules.vendor.pre_request.flask import filter_params

from app.models.account.user_location import UserLocationModel
from app.models.account.user_info import UserInfoModel

from app.helper.response import *


class ReportHandler(BaseHandler):

    rule = {
        "longitude": Rule(direct_type=float),
        "latitude": Rule(direct_type=float)
    }

    @filter_params(post=rule)
    def post(self, params):

        user_location = UserLocationModel()
        user_location.access_token = g.account.get("access_token")
        user_location.user_id = g.account.get("user_id")
        user_location.longitude = params["longitude"]
        user_location.latitude = params["latitude"]

        db.session.add(user_location)
        db.session.commit()

        # 更新用户信息
        if g.account["user_id"]:
            UserInfoModel.query.filter_by(user_id=g.account["user_id"]).update({"location_id": user_location.id})

        return json_success_response("")


common.add_url_rule("/location/report", view_func=ReportHandler.as_view("location_report"))
