import datetime
from app import db
from app.models.base.base import BaseModel


class OrderInfoModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_info"

    order_id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), default="")
    order_type = db.Column(db.Integer, default=0)
    market_price = db.Column(db.Integer, default=0)
    order_price = db.Column(db.Integer, default=0)
    order_discount_fee = db.Column(db.Integer, default=0)
    order_number = db.Column(db.Integer, default=1)
    order_fee = db.Column(db.Integer, default=0)
    address_id = db.Column(db.Integer, default=0)
    order_message = db.Column(db.String(255), default=0)
    pay_time = db.Column(db.DateTime, default=datetime.datetime.now)
    ship_time = db.Column(db.DateTime, default=datetime.datetime.now)
    receive_time = db.Column(db.DateTime, default=datetime.datetime.now)
    transaction_id = db.Column(db.String(45), default="")
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
    def query_order_info_model(order_id):
        if not order_id:
            return None

        if isinstance(order_id, list):
            result = OrderInfoModel.query.filter(OrderInfoModel.order_id.in_(order_id)).all()
            if not result:
                result = []
        else:
            result = OrderInfoModel.query.filter_by(order_id=order_id).first()
            if not result:
                result = None
        return result

    @staticmethod
    def query_order_info_with_order_no(order_no):
        return OrderInfoModel.query.filter_by(order_no=order_no).first()

    @staticmethod
    def update_order_info(order_id, params):
        """
        更新订单信息
        :param order_id: 订单id
        :param params: 需要修改的参数
        """
        if not order_id or not params:
            return

        OrderInfoModel.query.filter_by(order_id=order_id).update(params)
