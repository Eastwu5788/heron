import datetime
from app import db
from app.models.base.base import BaseModel


class ShareReportModel(db.Model, BaseModel):

    __bind_key__ = "a_social"
    __tablename__ = "share_report"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    report_name_id = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(50), default="")
    other_reason = db.Column(db.String(100), default="")
    status = db.Column(db.Integer, default=1)
    type = db.Column(db.Integer, default=1)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_share_report(user_id, report_user_id, report_type):
        """
        查询动态举报模型
        :param user_id: 用户id
        :param report_user_id: 被举报的用户id
        :param report_type: 举报类型
        """
        result = ShareReportModel.query.filter_by(user_id=user_id,
                                                  report_name_id=report_user_id,
                                                  type=report_type).first()
        if not result:
            return None

        return result
