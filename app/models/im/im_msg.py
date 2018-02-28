from datetime import datetime
from app import db
from app.models.base.base import BaseModel


class IMMsgModel(BaseModel, db.Model):

    __bind_key__ = "a_im"
    __tablename__ = "im_msg"

    msg_id = db.Column(db.Integer, primary_key=True)
    chatfrom = db.Column(db.Integer, default=0)
    chatto = db.Column(db.Integer, default=0)
    msg_type = db.Column(db.Integer, default=1)
    type = db.Column(db.Integer, default=1)
    content = db.Column(db.String(1000), default="")
    json_data = db.Column(db.String(500), default="")
    status = db.Column(db.Integer, default=1)

    pub_time = db.Column(db.DateTime, default=datetime.now)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, params):

        if params:
            for key, value in params.items():
                if not hasattr(self, key):
                    continue

                setattr(self, key, value)
            db.session.add(self)
            db.session.commit()
