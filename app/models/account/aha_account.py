import datetime
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
