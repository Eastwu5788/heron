import datetime
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
