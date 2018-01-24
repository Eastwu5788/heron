import datetime
from app import db, cache
from app.models.base.base import BaseModel

user_info_cache_key_by_id = "UserInfoModel:QueryByID:"


class UserInviteCodeModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_invite_code"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    code = db.Column(db.String(32), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_invite_code(user_id):
        """
        查询某一个用户的邀请码
        :param user_id: 用户的id
        """
        user_invite_model = UserInviteCodeModel.query.filter_by(user_id=user_id).first()
        if not user_invite_model:
            from app.helper.secret import get_seed

            user_invite_model = UserInviteCodeModel()
            user_invite_model.user_id = user_id
            user_invite_model.code = get_seed(str(user_id), 32)

            db.session.add(user_invite_model)
            db.session.commit()

        return user_invite_model.code
