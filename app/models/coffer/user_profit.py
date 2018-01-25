import datetime
from app.models.base.base import BaseModel
from app import db


class UserProfitModel(db.Model, BaseModel):
    __bind_key__ = "a_coffer"
    __tablename__ = "user_profit"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    money = db.Column(db.Integer, default=0)
    consumer_money = db.Column(db.Integer, default=0)
    today_money = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_profit(user_id):
        result = UserProfitModel.query.filter_by(user_id=user_id).first()
        return result
