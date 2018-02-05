import datetime
from app import db, cache
from app.models.base.base import BaseModel


class UserBlackModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_black"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    black_user_id = db.Column(db.Integer, default=0)

    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_black_list(user_id, status, offset, limit):
        query = UserBlackModel.query.filter_by(user_id=user_id, status=status).order_by(UserBlackModel.id.desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = query.all()
        if not result:
            result = []
        return result
