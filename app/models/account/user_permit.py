import datetime
from app import db, cache
from app.models.base.base import BaseModel


class UserPermitModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_permit"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    allow_post_txt = db.Column(db.Integer, default=0)
    allow_post_image = db.Column(db.Integer, default=0)
    allow_post_audio = db.Column(db.Integer, default=0)
    allow_post_video = db.Column(db.Integer, default=0)
    allow_post_poll = db.Column(db.Integer, default=0)
    allow_post_reward = db.Column(db.Integer, default=0)
    allow_post_cash_image = db.Column(db.Integer, default=0)
    allow_post_trade = db.Column(db.Integer, default=0)
    allow_post_activity = db.Column(db.Integer, default=0)
    allow_post_debate = db.Column(db.Integer, default=0)
    allow_post_share = db.Column(db.Integer, default=0)
    allow_post_wechat = db.Column(db.Integer, default=0)
    allow_post_live = db.Column(db.Integer, default=0)
    allow_post_livepost = db.Column(db.Integer, default=0)
    allow_visit = db.Column(db.Integer, default=0)
    allow_be_visited = db.Column(db.Integer, default=0)
    allow_invite = db.Column(db.Integer, default=0)
    allow_like = db.Column(db.Integer, default=0)
    allow_comment = db.Column(db.Integer, default=0)
    allow_vote = db.Column(db.Integer, default=0)
    allow_search = db.Column(db.Integer, default=0)
    allow_get_attach = db.Column(db.Integer, default=0)
    allow_get_image = db.Column(db.Integer, default=0)
    allow_transfer = db.Column(db.Integer, default=0)
    allow_top_up = db.Column(db.Integer, default=0)
    allow_withdraw = db.Column(db.Integer, default=0)
    allow_follow = db.Column(db.Integer, default=0)
    allow_send_pm = db.Column(db.Integer, default=0)
    allow_upload = db.Column(db.Integer, default=0)
    allow_appointment = db.Column(db.Integer, default=0)
    allow_reward = db.Column(db.Integer, default=0)
    min_trade_price = db.Column(db.Integer, default=0)
    max_trade_price = db.Column(db.Integer, default=0)
    min_reward_price = db.Column(db.Integer, default=0)
    max_reward_price = db.Column(db.Integer, default=0)
    max_friend_num = db.Column(db.Integer, default=0)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_permit_model(user_id):
        if not user_id:
            return None

        result = UserPermitModel.query.filter_by(user_id=user_id).first()
        return result
