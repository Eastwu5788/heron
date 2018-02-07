import datetime
from app import db
from app.models.base.base import BaseModel

from app.models.social.social_meta import  SocialMetaModel

from app.helper.utils import array_column


class FollowModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "follow"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    follow_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_follow_user_list(user_id):
        """
        查询某人关注的用户列表
        :param user_id: 用户id
        :return: 关注的用户列表
        """
        result = FollowModel.query.filter_by(user_id=user_id, status=1).all()
        if not result:
            result = []

        from app.helper.utils import array_column
        return array_column(result, "user_id")

    @staticmethod
    def query_follow_list(params):
        user_id = params["user_id"]
        if not user_id:
            return []

        query = FollowModel.query.filter_by(user_id=user_id, status=1)
        if params["last_id"]:
            query = query.filter(FollowModel.id<params["last_id"])

        query = query.order_by(FollowModel.id.desc())
        if params["limit"]:
            query = query.limit(params["limit"])

        result = query.all()
        if not result:
            result = []
        return result

    @staticmethod
    def query_fans_list(params):
        user_id = params["user_id"]
        if not user_id:
            return []

        query = FollowModel.query.filter_by(follow_id=user_id, status=1)
        if params["last_id"]:
            query = query.filter(FollowModel.id < params["last_id"])

        query = query.order_by(FollowModel.id.desc())
        if params["limit"]:
            query = query.limit(params["limit"])

        result = query.all()
        if not result:
            result = []
        return result

    @staticmethod
    def query_friends_list(params):
        user_id = params["user_id"]
        if not user_id:
            return []

        sql = "SELECT t1.* FROM a_social.follow t1, a_social.follow t2 WHERE t1.user_id = t2.follow_id AND t1.follow_id = t2.user_id AND t1.status = 1 AND t2.status = 1 AND t1.user_id = "
        sql += str(params["user_id"])

        if params["last_id"]:
            sql += " AND t1.id < " + str(params["last_id"])

        sql += " ORDER BY t1.id DESC"

        if params["limit"]:
            sql += " LIMIT " + str(params["limit"])

        from heron import app
        result_dict_list = db.session.execute(sql, bind=db.get_engine(app=app, bind='a_social')).fetchall()
        if not result_dict_list:
            result_dict_list = []

        result = []
        for item in result_dict_list:
            model = FollowModel()
            model.id = item[0]
            model.user_id = item[1]
            model.follow_id = item[2]
            model.status = item[3]
            result.append(model)

        return result

    @staticmethod
    def query_user_follow(user_id=0, follow_id=0):
        """
        查询某人关注某个人的模型
        :param user_id: 用户id
        :param follow_id: 关注的用户id
        """
        user_follow_model = FollowModel.query.filter_by(user_id=user_id, follow_id=follow_id).first()
        return user_follow_model

    @staticmethod
    def cancel_user_follow(user_id, follow_id):
        """
        取消关注某一个用户
        :param user_id: 当前用户
        :param follow_id: 关注的用户
        :return:
        """
        FollowModel.query.filter_by(user_id=user_id, follow_id=follow_id).update(dict(status=0))
        SocialMetaModel.update_social_meta_model(user_id, ["following"], False)
        SocialMetaModel.update_social_meta_model(follow_id, ["follower"], False)

    @staticmethod
    def query_relation_to_user(user_id, other_user_id):
        if user_id == other_user_id:
            return 1

        follow = FollowModel.query.filter_by(user_id=user_id, follow_id=other_user_id, status=1).first()
        fans = FollowModel.query.filter_by(user_id=other_user_id, follow_id=user_id, status=1).first()
        if follow and fans:
            return 4
        elif follow:
            return 2
        elif fans:
            return 3
        else:
            return 0

    @staticmethod
    def query_relation_to_user_list(user_id, other_user_id_list=()):
        """
        查询两个人的关注关系
        0->无关系 1->自己 2->我关注她 3->他关注我 4->互相关注
        """
        fans_list = FollowModel.query_relation_fans(user_id, other_user_id_list)
        follow_list = FollowModel.query_relation_follows(user_id, other_user_id_list)

        result = dict()
        for other_user_id in other_user_id_list:
            if other_user_id in fans_list and other_user_id in follow_list:
                result[other_user_id] = 4
            elif other_user_id in fans_list:
                result[other_user_id] = 3
            elif other_user_id in follow_list:
                result[other_user_id] = 2
            else:
                result[other_user_id] = 0

        if user_id in other_user_id_list:
            result[user_id] = 1

        return result

    @staticmethod
    def query_relation_follows(user_id, follow_list=()):
        follow_list = FollowModel.query.filter_by(user_id=user_id, status=1).filter(FollowModel.follow_id.in_(follow_list)).all()
        if not follow_list:
            follow_list = []
        return array_column(follow_list, "follow_id")

    @staticmethod
    def query_relation_fans(user_id, fans_list=()):
        """
        查询某一个用户的粉丝列表
        :param user_id: 用户id
        :param fans_list: 粉丝id
        """
        fans_list = FollowModel.query.filter_by(follow_id=user_id, status=1).filter(FollowModel.user_id.in_(fans_list)).all()
        if not fans_list:
            fans_list = []
        return array_column(fans_list, "user_id")