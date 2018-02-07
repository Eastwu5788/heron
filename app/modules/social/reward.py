from . import social
from app.modules.base.base_handler import BaseHandler

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.reward_icon import RewardIconModel

from app.helper.auth import login_required
from app.helper.response import json_success_response


class IconHandler(BaseHandler):

    rule = {
        "type": Rule(direct_type=int),
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        reward_icon_list = RewardIconModel.query_icons_with_type(params["type"])

        result = list()
        for icon_model in reward_icon_list:
            item = icon_model.to_dict(filter_params=True)
            item["price"] /= 100
            result.append(item)

        return json_success_response(result)


social.add_url_rule("/reward/geticon", view_func=IconHandler.as_view("reward_get_icon"))
