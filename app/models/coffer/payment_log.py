import datetime
from app.models.base.base import BaseModel
from app import db


class PaymentLogModel(db.Model, BaseModel):
    __bind_key__ = "a_coffer"
    __tablename__ = "payment_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    pay_id = db.Column(db.Integer, default=0)
    channel_type = db.Column(db.String(10), default="")
    transaction_type = db.Column(db.String(10), default="")
    transaction_id = db.Column(db.String(45), default="")
    transaction_fee = db.Column(db.Integer, default=0)
    trade_success = db.Column(db.Integer, default=0)
    message_detail = db.Column(db.String(500), default="")
    optional = db.Column(db.String(255), default="")
    callback_time = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, params):

        if params:
            for key, value in params.items():
                if not hasattr(self, key):
                    continue

                setattr(self, key, value)
            db.session.add(self)
            db.session.commit()
