import random
from flask import g
from . import social
from config.setting import SERVICE_ACCOUNT_LIST
from app.modules.base.base_handler import BaseHandler
from app.models.account.user_id_relation import UserIdRelationModel
from app.helper.auth import login_required
from app.helper.response import *


class ThrowHandler(BaseHandler):

    @login_required
    def get(self):

        count = UserIdRelationModel.query_user_id_relation_count()
        while True:
            index = random.randint(0, count-1)

            relation_model = UserIdRelationModel.query.filter_by(id=index).first()
            if relation_model and relation_model.user_id not in SERVICE_ACCOUNT_LIST and relation_model.user_id != g.account["user_id"]:
                str_id = relation_model.str_id
                break

        return json_success_response({"huanxin_uid": str_id, "content": "Hello ~"})


social.add_url_rule("/driftingbottle/throw", view_func=ThrowHandler.as_view("driftingbottle_throw"))

