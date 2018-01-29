import datetime
from app.models.base.base import BaseModel
from app import db


class VisitorRecordModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "visitor_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    visitor_user_id = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, user_id=0, visitor_user_id=0):

        # 用户存在的话，自动创建
        if user_id and visitor_user_id:
            self.user_id = user_id
            self.visitor_user_id = visitor_user_id

            db.session.add(self)
            db.session.commit()
