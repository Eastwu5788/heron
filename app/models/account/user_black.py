import datetime
from app import db, cache
from app.models.base.base import BaseModel

from app.models.account.user_info import UserInfoModel
from app.models.social.follow import FollowModel


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

    @staticmethod
    def check_black_status(user_id, black_user_id):
        """
        检查两个人是否有拉黑关系
        0->无关系 1->我拉黑他 2->他拉黑我 3->互相拉黑
        :param user_id: 我的用户id
        :param black_user_id: 其他人的用户id
        :return: int
        """
        query = UserBlackModel.query.filter_by(status=1).filter(UserBlackModel.user_id.in_([user_id, black_user_id]))
        result = query.filter(UserBlackModel.black_user_id.in_([user_id, black_user_id])).all()

        code = 0
        for model in result:
            if model.user_id == user_id and model.black_user_id == black_user_id:
                code += 1
            if model.user_id == black_user_id and model.black_user_id == user_id:
                code += 2

        return code

    @staticmethod
    def update_black_status(user_id, black_user_id, status):
        if status == 1:
            # 当前用户不允许被拉黑
            result = UserBlackModel.black_able(black_user_id)
            if not result:
                result = UserBlackModel.black_user(user_id, black_user_id)
        elif status == 0:
            result = UserBlackModel.cancel_back_user(user_id, black_user_id)
        return result

    @staticmethod
    def black_able(black_user_id):
        user = UserInfoModel.query_user_model_by_id(black_user_id)
        user_info = UserInfoModel.format_user_info(user)

        if user_info and user_info.get("role_id", 0) == 8:
            return {"data": 0, "message": "不能拉黑系统管理员"}
        return None

    @staticmethod
    def cancel_back_user(user_id, black_user_id):
        user_black = UserBlackModel.query.filter_by(user_id, black_user_id).first()
        if not user_black or user_black.status != 1:
            return {"data": 0, "message": "当前未拉黑该用户"}
        user_black.status = 0
        db.session.commit()
        return {"data": 1, "message": "取消拉黑成功"}

    @staticmethod
    def black_user(user_id, black_user_id):
        user_black = UserBlackModel.query.filter_by(user_id, black_user_id).first()

        if not user_black:
            user_black = UserBlackModel()
            user_black.user_id = user_id
            user_black.black_user_id = black_user_id
            user_black.status = 1

            db.session.add(user_black)
        else:
            if user_black.status == 1:
                return {"data": 0, "message": "不能重复拉黑"}
            user_black.status = 1
        try:
            db.session.commit()
        except:
            return {"data":0, "message": "拉黑失败"}

        # 取消关注
        follow = FollowModel.query_relation_to_user(user_id, black_user_id)
        if follow in (2, 4):



        return {"data": 1, "message": "拉黑成功"}
