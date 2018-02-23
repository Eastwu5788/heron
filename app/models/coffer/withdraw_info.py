import time
from datetime import datetime
from app import db
from app.models.base.base import BaseModel


class WithdrawInfoModel(db.Model, BaseModel):

    __bind_key__ = "a_coffer"
    __tablename__ = "withdraw_info"

    __fillable__ = ["withdraw_id", "cash_amount", "note", "status", "created_time", "updated_time"]

    withdraw_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    account_id = db.Column(db.Integer, default=0)
    cash_amount = db.Column(db.Integer, default=0)
    note = db.Column(db.String(255), default="")
    type = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def check_withdraw_enable(user_id):
        time_str = time.strftime("%Y-%m-%d", time.time())
        with_info = WithdrawInfoModel.query.filter_by(user_id=user_id).filter(WithdrawInfoModel.created_time >= time_str).first()
        if with_info:
            return False
        return True

    @staticmethod
    def query_withdraw_info_list(user_id, params):
        query = WithdrawInfoModel.query.filter_by(user_id=user_id)

        status = params.get("status", None)
        if status:
            if isinstance(status, list):
                query = query.filter(WithdrawInfoModel.status.in_(status))
            else:
                query = query.filter_by(status=status)

        if params.get("last_id", 0) > 0:
            query = query.filter(WithdrawInfoModel.withdraw_id < params["last_id"])

        result = query.order_by(WithdrawInfoModel.withdraw_id.desc()).limit(20).all()
        if not result:
            result = []

        return result

    @staticmethod
    def format_withdraw_model(withdraw_list):
        result = list()

        if not withdraw_list:
            return result

        for model in withdraw_list:
            item = model.to_dict(filter_params=True)
            item["cash_amount"] = model.cash_amount / 100
            item["status_message"] = WithdrawInfoModel.format_withdraw_status(model.status)
            result.append(item)

        return result

    @staticmethod
    def format_withdraw_status(status):
        if status == 1:
            return "待审核"
        elif status == 2:
            return "提现中"
        elif status == 3:
            return "已提现"
        elif status == 9:
            return "已取消"
        else:
            return "错误状态"
