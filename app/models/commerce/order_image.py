import datetime
from app import db
from app.models.base.base import BaseModel


class OrderImageModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_image"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, default=0)
    buyer_id = db.Column(db.Integer, default=0)
    image_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)

    @staticmethod
    def query_invalid_order_list(seller_id, buyer_id):
        """
        查询所有失效订单
        :param seller_id: 卖家
        :param buyer_id: 买家
        """
        invalid_order_list = OrderImageModel.query.filter_by(seller_id=seller_id, buyer_id=buyer_id, status=3).all()
        if not invalid_order_list:
            invalid_order_list = []
        return invalid_order_list
