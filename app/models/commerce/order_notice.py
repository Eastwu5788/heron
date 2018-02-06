import datetime
from app import db
from app.models.base.base import BaseModel


class OrderNoticeModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_notice"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_order_notice(order_id, user_id):
        result = OrderNoticeModel.query.filter_by(order_id=order_id, user_id=user_id, status=1).first()
        return result
