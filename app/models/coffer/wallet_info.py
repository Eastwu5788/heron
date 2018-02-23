import datetime
from app import db
from app.models.base.base import BaseModel


class WalletInfoModel(db.Model, BaseModel):

    __bind_key__ = "a_coffer"
    __tablename__ = "wallet_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    wallet_name = db.Column(db.String(10), default="")
    balance = db.Column(db.Integer, default=0)
    balance_useable = db.Column(db.Integer, default=0)
    balance_freeze = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_wallet(user_id):
        wallet = WalletInfoModel.query.filter_by(user_id=user_id, status=1).first()
        return wallet
