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

    def __init__(self, params):

        if params:
            for key, value in params.items():
                if not hasattr(self, key):
                    continue
                setattr(self, key, value)
            db.session.add(self)
            db.session.commit()

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

    @staticmethod
    def query_order_with_others(user_id, other_user_id, per_page=20, last_id=0, is_read=True):
        """
        查询我与另外一个人的所有已完成的订单信息
        :param user_id: 我的id
        :param other_user_id: 其它人的id
        :param per_page: 分页
        :param last_id: 最后一笔订单的id
        :param is_read: 是否包含红包照片
        """
        query = OrderMetaModel.query.filter_by(seller_id=user_id)

        if other_user_id:
            query = query.filter_by(buyer_id=other_user_id)

        if last_id:
            query = query.filter(OrderMetaModel.id < last_id)

        if not is_read:
            query = query.filter(OrderMetaModel.product_type != 11)

        result = query.filter_by(order_status=6).order_by(OrderMetaModel.id.desc()).limit(per_page).all()
        if not result:
            result = []
        return result
