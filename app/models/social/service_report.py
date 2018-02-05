import datetime
from app.models.base.base import BaseModel
from app import db


class ServiceReportModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "service_report"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    report_user_id = db.Column(db.Integer, default=0)
    service_id = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(50), default="")
    message = db.Column(db.String(100), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_service_report(user_id, report_user_id, order_id):
        if not user_id or not report_user_id or not order_id:
            return None

        query = ServiceReportModel.query.filter_by(user_id=user_id, report_user_id=report_user_id, order_id=order_id)
        return query.filter_by(status=1).first()
