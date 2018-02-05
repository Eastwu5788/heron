import datetime
from app.models.base.base import BaseModel
from app import db


class WeChatWantBuyModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "wechat_want_buy"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, default=0)
    buyer_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_wechat_want_buy(seller_id, buyer_id):
        return WeChatWantBuyModel.query.filter_by(buyer_id=buyer_id, seller_id=seller_id,  status=1).first()
