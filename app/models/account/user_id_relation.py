import datetime
from sqlalchemy import func
from app import db, cache
from app.models.base.base import BaseModel

user_id_relation_cache_key = "UserIdRelationModel:QueryRelationById:"


class UserIdRelationModel(db.Model, BaseModel):
    __bind_key__ = "a_account"
    __tablename__ = "user_id_relation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)

    str_id = db.Column(db.String(32), default="")

    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_user_id_relation(user_id, refresh=False):

        cache_key = user_id_relation_cache_key + str(user_id)

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        model = UserIdRelationModel.query.filter_by(user_id=user_id, status=1).first()
        if model:
            cache.set(cache_key, model)
        return model

    @staticmethod
    def query_user_id_relation_count():
        """统计数量"""
        return db.session.query(func.count(UserIdRelationModel.id)).scalar()

    @staticmethod
    def query_user_by_ease_mob_id(ease_mob_id, refresh=False):
        if not ease_mob_id:
            return None

        cache_key = user_id_relation_cache_key + ease_mob_id

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = UserIdRelationModel.query.filter_by(str_id=ease_mob_id, status=1).first()
        if result:
            cache.set(cache_key, result)
        return result
