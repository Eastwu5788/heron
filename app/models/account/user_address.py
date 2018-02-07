import datetime
from collections import OrderedDict
from sqlalchemy.sql import text
from app import db, cache
from app.models.base.base import BaseModel


class UserAddressModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_address"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    address_name = db.Column(db.String(50), default="")
    email = db.Column(db.String(50), default="")
    consignee = db.Column(db.String(30), default="")
    country = db.Column(db.Integer, default=0)
    province = db.Column(db.Integer, default=0)
    city = db.Column(db.Integer, default=0)
    district = db.Column(db.Integer, default=0)
    address = db.Column(db.String(100), default=100)
    zipcode = db.Column(db.String(20), default="")
    tel = db.Column(db.String(20), default="")
    mobile = db.Column(db.String(20), default="")
    sign_building = db.Column(db.String(100), default="")
    best_time = db.Column(db.String(100), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, params=OrderedDict()):

        if params:
            for key, value in params.items():
                setattr(self, key, value)
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def query_user_address(user_id, params=OrderedDict()):
        query = UserAddressModel.query.filter_by(user_id=user_id)

        for key, value in params.items():
            query = query.filter(text("%s=:%s" % (key, key)))

        return query.params(params).first()
