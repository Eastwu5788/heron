import datetime
from app import db, cache
from app.models.base.base import BaseModel

remark_cache_key = "RemarkNameModel:User:"


class RemarkNameModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "remark_name"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    remark_user_id = db.Column(db.Integer, default=0)
    remark_nickname = db.Column(db.String(40), default="")
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)

    @staticmethod
    def query_remark_name(user_id, remark_user_id, refresh=False):
        """
        查询我给其它用户备注的昵称
        :param user_id: 我的id
        :param remark_user_id: 被我备注的用户id
        :param refresh: 刷新缓存
        """

        cache_key = remark_cache_key + str(user_id) + ":" + str(remark_user_id)
        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = RemarkNameModel.query.filter_by(user_id=user_id, remark_user_id=remark_user_id, status=1).first()
        if result:
            cache.set(cache_key, result)
        return result
