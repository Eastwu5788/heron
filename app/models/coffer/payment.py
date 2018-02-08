import datetime
from app.models.base.base import BaseModel
from app import db


class PaymentModel(db.Model, BaseModel):
    __bind_key__ = "a_coffer"
    __tablename__ = "payment"

    pay_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    wallet_id = db.Column(db.Integer, default=0)
    purpose = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    order_no = db.Column(db.String(32), default="")
    fee_type = db.Column(db.String(3), default="")
    total_fee = db.Column(db.Integer, default=0)
    cash_fee = db.Column(db.Integer, default=0)
    coupon_fee = db.Column(db.Integer, default=0)
    coupon_count = db.Column(db.Integer, default=0)
    pay_method = db.Column(db.Integer, default=0)
    pay_desc = db.Column(db.String(255), default="")
    status = db.Column(db.Integer, default=1)
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
