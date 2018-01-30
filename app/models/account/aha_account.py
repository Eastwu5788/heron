import datetime
import re
from app import db
from app.models.base.base import BaseModel


class AhaAccountModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "aha_account"

    __fillable__ = ["aha_id", "changeable_aha"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    aha_id = db.Column(db.String(20), default="")
    changeable_aha = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_aha_account_by_id(user_id=0, auto_formated=True):
        aha_account_model = AhaAccountModel.query.filter_by(user_id=user_id, status=1).first()

        if not auto_formated:
            return aha_account_model

        return aha_account_model.to_dict(filter_params=True)

    @staticmethod
    def query_aha_account_by_aha_id(aha_id):
        aha_account_model = AhaAccountModel.query.filter_by(aha_id=aha_id, status=1).first()
        return aha_account_model

    @staticmethod
    def update_aha_id(user_id, aha_id):
        if not user_id or not aha_id:
            return False

        account_model = AhaAccountModel.query.filter_by(user_id=user_id, status=1).first()
        if not account_model:
            account_model = AhaAccountModel()
            account_model.user_id = user_id
            account_model.aha_id = aha_id
            account_model.changeable_aha = 0
            account_model.status = 1

            db.session.add(account_model)
        else:
            if account_model.changeable_aha == 1:
                account_model.aha_id = aha_id
                account_model.changeable_aha = 0
            elif account_model.aha_id == aha_id:
                return True
            else:
                return False
        db.session.commit()
        return True

    @staticmethod
    def check(aha_id):

        result = {
            "success": True,
            "message": "aha号萌萌哒~",
        }

        if len(aha_id) > 20 or len(aha_id) < 5:
            result["success"] = False
            result["message"] = "aha号长度要求5-20位"
            return result

        if " " in aha_id:
            result["success"] = False
            result["message"] = "aha号不能有空格"
            return result

        if not re.match('[a-zA-Z]', aha_id) and not re.match('\d', aha_id):
            result["success"] = False
            result["message"] = "aha号中必须包含数字或字母"

        if not re.match('^[a-zA-Z\d\-_]+$', aha_id):
            result["success"] = False
            result["message"] = "aha号只能使用数字、字母、-、_"

        return result
