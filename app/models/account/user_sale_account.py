import datetime
from app import db
from app.models.base.base import BaseModel


class UserSaleAccountModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_seal_account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    udid = db.Column(db.String(40), default="")
    mobile = db.Column(db.String(15), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def check_banned(mobile="", udid="", user_id=0):
        """
        检查用户账号是否被封禁
        """
        query = UserSaleAccountModel.query.filter_by(status=1)
        if mobile:
            result = query.filter_by(mobile=mobile).first()
            if result:
                return True
        elif udid:
            result = query.filter_by(udid=udid).first()
            if result:
                return True
        elif user_id:
            result = query.filter_by(user_id=user_id).first()
            if result:
                return True
        return False
