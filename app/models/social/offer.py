import datetime
from app.models.base.base import BaseModel
from app import db


class OfferModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "offer"

    offer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    present_id = db.Column(db.Integer, default=0)
    total_number = db.Column(db.Integer, default=0)
    join_number = db.Column(db.Integer, default=0)
    winner_user_id = db.Column(db.Integer, default=0)
    offer_status = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.datetime.now)
    due_time = db.Column(db.DateTime, default=datetime.datetime.now)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_offer_model(share_id):
        return OfferModel.query.filter_by(share_id=share_id).first()
