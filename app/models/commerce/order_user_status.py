import datetime
from app import db
from app.models.base.base import BaseModel


class OrderUserStatusModel(db.Model, BaseModel):
    __bind_key__ = "a_commerce"
    __tablename__ = "order_user_status"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
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
