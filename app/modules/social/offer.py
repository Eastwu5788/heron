from flask import g
from . import social
from app import db
from app.modules.base.base_handler import BaseHandler

from app.models.social.offer_list import OfferListModel
from app.models.social.offer import OfferModel
from app.models.social.share import ShareModel

from app.modules.vendor.pre_request import filter_params, Rule
from app.helper.auth import login_required
from app.helper.response import *


class GetListHandler(BaseHandler):

    rule = {
        "offer_id": Rule(direct_type=int),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        offer_list = OfferListModel.query_offer_list(params["offer_id"], params["last_id"], 20)
        return json_success_response(offer_list)


class EnterHandler(BaseHandler):

    rule = {
        "share_id": Rule(direct_type=int),
        "offer_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        enable, msg = OfferModel.check_offer_enter_enable(params["offer_id"], g.account["user_id"])
        if not enable:
            return json_success_response({"data": 0, "message": msg})

        offer = OfferModel.query_offer_mode_with_offer_id(params["offer_id"])

        offer_list = OfferListModel()
        offer_list.user_id = offer.user_id
        offer_list.share_id = offer.share_id
        offer_list.offer_id = offer.offer_id
        offer_list.apply_user_id = g.account["user_id"]
        offer_list.status = 1
        db.session.add(offer_list)

        offer.join_number += 1

        db.session.commit()
        return json_success_response({"data": 1, "message": "报名成功"})


class GetMyOfferHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int, allow_empty=True, default=0),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        if not params["user_id"]:
            params["user_id"] = g.account["user_id"]

        share_list = ShareModel.query_offer_share_list(params["user_id"], params["last_id"])
        return json_success_response(ShareModel.format_share_model(share_list, g.account["user_id"]))


class ChooseHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int),
        "offer_id": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        offer = OfferModel.query_offer_mode_with_offer_id(params["offer_id"])

        if offer.user_id != g.account["user_id"]:
            return json_fail_response(2128)

        if offer.offer_status == 3:
            return json_fail_response(2129)

        if offer.winner_user_id:
            return json_fail_response(2130)

        if not OfferListModel.check_offer_enter_status(params["offer_id"], params["user_id"]):
            return json_fail_response(2131)

        success, message = OfferModel.choose_winner(params["offer_id"], params["user_id"])
        if success:
            return json_success_response({"data": 1, "message": "成功"})
        else:
            return json_success_response({"data": 0, "message": message})


social.add_url_rule("/offer/getlist", view_func=GetListHandler.as_view("offer_get_list"))
social.add_url_rule("/offer/enter", view_func=EnterHandler.as_view("offer_enter"))
social.add_url_rule("/offer/getmyoffer", view_func=GetMyOfferHandler.as_view("offer_get_my_offer"))
social.add_url_rule("/offer/choose", view_func=ChooseHandler.as_view("offer_choose"))

