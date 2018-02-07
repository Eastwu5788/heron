import datetime
from app.models.base.base import BaseModel
from app import db


class UserIncomeModel(db.Model, BaseModel):
    __bind_key__ = "a_coffer"
    __tablename__ = "user_income"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    invite_uid = db.Column(db.Integer, default=0)
    cash_amount = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=1)
    balance = db.Column(db.Integer, default=0)
    note = db.Column(db.String(255), default="")
    order_id = db.Column(db.Integer, default=0)
    pay_id = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_order_income_list(user_id, order_id_list=list()):
        if not user_id or not order_id_list:
            return []

        query = UserIncomeModel.query.filter_by(user_id=user_id).filter(UserIncomeModel.order_id.in_(order_id_list))
        result = query.order_by(UserIncomeModel.order_id.desc()).all()
        if not result:
            result = []
        return result
