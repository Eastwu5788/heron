import json
from flask import g
from . import user
from app import db
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule, Range

from app.models.account.user_permit import UserPermitModel
from app.models.account.user_wechat import UserWeChatModel
from app.models.account.user_info import UserInfoModel
from app.models.account.user_wechat import UserWeChatModel
from app.models.commerce.order_meta import OrderMetaModel

from app.helper.auth import login_required
from app.helper.response import *


class AddHandler(BaseHandler):

    max_upload_image_count = 6

    rule = {
        "wechat": Rule(reg=r"^[_a-zA-Z0-9]{5,20}$"),
        "price": Rule(direct_type=float, range=Range(99, 1314))
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        permit = UserPermitModel.query_user_permit_model(g.account["user_id"])
        if permit and permit.allow_post_wechat == 0:
            return json_fail_response(2408)

        wechat = UserWeChatModel()
        wechat.user_id = g.account["user_id"]
        wechat.wechat = params["wechat"]
        wechat.price = params["price"] * 100
        wechat.status = 1

        db.session.add(wechat)

        try:
            db.session.commit()
            UserInfoModel.query_user_model_by_id(g.account["user_id"], True)
            return json_success_response({
                "data": 1,
                "message": "设置成功",
            })
        except:
            return json_success_response({
                "data": 0,
                "message": "设置失败",
            })


class SoldListHandler(BaseHandler):

    rule = {
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        query = OrderMetaModel.query.filter_by(seller_id=g.account["user_id"], product_type=80)
        query = query.filter(OrderMetaModel.order_status.in_([2, 3, 5, 6]), OrderMetaModel.ship_status.in_([0, 2, 3]))
        if params["last_id"]:
            query = query.filter(OrderMetaModel.id < params["last_id"])
        order_meta_list = query.order_by(OrderMetaModel.id.desc()).limit(20).all()
        result = UserWeChatModel.format_user_wechat_data(order_meta_list, {"user_id", g.account["user_id"]}, "seller_id", "buyer_id")
        return json_success_response(result)


user.add_url_rule("/wechat/getsoldlist/", view_func=SoldListHandler.as_view("get_sold_list"))
user.add_url_rule("/wechat/add", view_func=AddHandler.as_view("user_wechat_add"))

