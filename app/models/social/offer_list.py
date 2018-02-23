from datetime import datetime
from app import db
from app.models.base.base import BaseModel
from app.models.account.user_info import UserInfoModel


class OfferListModel(db.Model, BaseModel):

    __bind_key__ = "a_social"
    __tablename__ = "offer_list"

    __fillable__ = ["id", "win", "status"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    offer_id = db.Column(db.Integer, default=0)
    apply_user_id = db.Column(db.Integer, default=0)
    win = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def check_offer_enter_status(offer_id, user_id):
        offer_enter = OfferListModel.query.filter_by(offer_id=offer_id, apply_user_id=user_id).first()
        return offer_enter

    @staticmethod
    def query_offer_list(offer_id, last_id=0, limit=3):
        if not offer_id:
            return list()

        query = OfferListModel.query.filter_by(offer_id=offer_id)

        if last_id:
            query = query.filter(OfferListModel.id < last_id)

        result = query.order_by(OfferListModel.id.desc()).limit(limit).all()
        if not result:
            result = list()

        return OfferListModel.format_offer_list(result)

    @staticmethod
    def format_offer_list(offer_list):
        result = list()
        if not offer_list:
            return result

        for offer_list_model in offer_list:
            item = offer_list_model.to_dict(filter_params=True)
            user_info = UserInfoModel.query_user_model_by_id(offer_list_model.apply_user_id)
            item["user_info"] = UserInfoModel.format_user_info(user_info)
            result.append(item)

        return result

    @staticmethod
    def choose_winner(offer_id, user_id):
        if not offer_id or not user_id:
            return False

        OfferListModel.query.filter_by(offer_id=offer_id, apply_user_id=user_id).update(dict(win=1))
