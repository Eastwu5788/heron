import datetime
from sqlalchemy import text
from collections import OrderedDict
from app import db
from app.models.base.base import BaseModel


class OrderMetaModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_meta"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, default=0)
    buyer_id = db.Column(db.Integer, default=0)
    product_type = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, default=0)
    order_status = db.Column(db.Integer, default=0)
    pay_status = db.Column(db.Integer, default=0)
    ship_status = db.Column(db.Integer, default=0)
    rate_status = db.Column(db.Integer, default=0)
    comment_status = db.Column(db.Integer, default=0)
    complain_status = db.Column(db.Integer, default=0)
    invoice_status = db.Column(db.Integer, default=0)
    service_status = db.Column(db.Integer, default=0)
    pay_id = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_order_meta_model(seller_id, buyer_id, product_type, pay_status):
        query = OrderMetaModel.query.filter_by(seller_id=seller_id, buyer_id=buyer_id, product_type=product_type)
        result = query.filter(pay_status=pay_status).order_by(OrderMetaModel.id.desc()).first()
        return result

    @staticmethod
    def query_order_meta(params=OrderedDict()):

        query = OrderMetaModel.query

        for key, value in params.items():
            query = query.filter(text("%s=:%s" % (key, key)))

        result = query.params(params).first()
        if not result:
            result = None

        return result
