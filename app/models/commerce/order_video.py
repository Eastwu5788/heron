import datetime
from app import db
from app.models.base.base import BaseModel


class OrderVideoModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_video"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, default=0)
    buyer_id = db.Column(db.Integer, default=0)
    video_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)

    @staticmethod
    def query_order_video_list(user_id, video_id_list):
        if not video_id_list or not user_id:
            return []
        result = OrderVideoModel.query.filter_by(buyer_id=user_id, status=2).filter(OrderVideoModel.video_id.in_(video_id_list)).all()
        if not result:
            result = []
        return result

    @staticmethod
    def query_invalid_order_video_list(user_id, visitor_user_id):
        invalid_video_list = OrderVideoModel.query.filter_by(seller_id=user_id, buyer_id=visitor_user_id, status=3).all()
        if not invalid_video_list:
            invalid_video_list = []
        return invalid_video_list

