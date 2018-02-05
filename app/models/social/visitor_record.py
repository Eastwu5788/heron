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

    @staticmethod
    def query_visitor_list_by_day(user_id, per_page, last_id=0):
        day = datetime.datetime.now() - datetime.timedelta(days=last_id)
        start_time = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        end_time = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)

        print(start_time)
        print(end_time)

        query = VisitorRecordModel.query.filter_by(user_id=user_id).filter(VisitorRecordModel.visitor_user_id != user_id)
        query = query.filter(VisitorRecordModel.created_time >= start_time, VisitorRecordModel.created_time <= end_time)

        result = query.order_by(VisitorRecordModel.id.desc()).all()
        if result and len(result) > per_page:
            result = result[0:per_page]
        return result

