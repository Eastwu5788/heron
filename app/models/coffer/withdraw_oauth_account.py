from datetime import datetime
from app import db
from app.models.base.base import BaseModel


class WithdrawOauthAccountModel(db.Model, BaseModel):

    __bind_key__ = "a_coffer"
    __tablename__ = "withdraw_oauth_account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(15), default="")
    account = db.Column(db.String(20), default="")
    nickname = db.Column(db.String(40), default="")
    type = db.Column(db.Integer, default=0)
    openid = db.Column(db.String(40), default="")
    status = db.Column(db.Integer, default=0)

    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def query_withdraw_oauth_account(user_id, auth_type):
        result = WithdrawOauthAccountModel.query.filter_by(user_id=user_id, type=auth_type, status=1).first()
        return result
