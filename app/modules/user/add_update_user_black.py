from app.modules.base.base_handler import BaseHandler
from . import user

from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.helper.auth import login_required

class IndexHandler(BaseHandler):

    rule = {
        "black_user_id": Rule(direct_type=int),
        "status": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
