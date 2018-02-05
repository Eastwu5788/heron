import datetime
from app import db
from app.models.base.base import BaseModel


class CommentRelationModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "my_comment_relation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    reply_user_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, default=0)
    reply_comment_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, user_id, reply_user_id, share_id, comment_id, reply_comment_id):
        self.user_id = user_id
        self.reply_user_id = reply_user_id
        self.share_id = share_id
        self.comment_id = comment_id
        self.reply_comment_id = reply_comment_id

        if self.reply_user_id:
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def query_relation_info(user_id, per_page=10, last_cid=0):
        query = CommentRelationModel.query.filter(CommentRelationModel.reply_user_id == user_id,
                                                  CommentRelationModel.status != 0)
        if last_cid:
            query = query.filter(CommentRelationModel.comment_id < last_cid)

        result = query.order_by(CommentRelationModel.id.desc()).order_by(CommentRelationModel.id.desc()).limit(per_page).all()
        if not result:
            result = []
        return result
