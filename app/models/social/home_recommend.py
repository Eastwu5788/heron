import datetime
from sqlalchemy import or_, and_
from app import db, cache
from app.models.base.base import BaseModel
from app.models.core.open_log import OpenLogModel

home_recommend_top_cache_key = "HomeRecommend:Top:Home:Users"
home_recommend_top_cache_time = 60 * 10

home_recommend_random_cache_key = "HomeRecommend:Random:Home:Users"


class HomeRecommendModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "home_recommend"
    __table_args__ = {'schema': 'a_social'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(OpenLogModel.user_id), default=0)
    sort = db.Column(db.Integer, default=0)
    type_id = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    gender = db.Column(db.Integer, default=0)
    image_id = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_home_top_users(refresh=False):
        if not refresh:
            users = cache.get(home_recommend_top_cache_key)
            if users:
                return users

        users = HomeRecommendModel.query.filter_by(type_id=1, postion=1, status=1).all()
        if users:
            cache.set(home_recommend_top_cache_key, users, home_recommend_top_cache_time)
        return users

    @staticmethod
    def query_home_random_users(params):
        result = HomeRecommendModel.query_random_list(params)

        if len(result) == params.get("limit", 20):
            return result

        if params["last_id"] > params["offset"] or params["last_id"] == 0:
            params["last_id"] = 0.5
            params["limit"] = params["limit"] - len(result)
        else:
            return result

        result_ext = HomeRecommendModel.query_random_list(params)
        return result + result_ext

    @staticmethod
    def query_random_list(params):
        query = HomeRecommendModel.query.filter_by(position=params["position"], type_id=params["type_id"], status=1)

        active_list = params.get("active_list", None)
        if active_list:
            query = query.filter(HomeRecommendModel.user_id.notin_(active_list))

        offset = params.get("offset", 0)
        last_id = params.get("last_id", 0)
        if offset > 0:
            if last_id == 0:
                query = query.filter(HomeRecommendModel.id > offset)
            elif last_id > offset:
                query = query.filter(HomeRecommendModel.id > last_id)
            else:
                query = query.filter(HomeRecommendModel.id > last_id, HomeRecommendModel.id <= offset)

        result = query.order_by(HomeRecommendModel.id.asc()).limit(params.get("limit", 20)).all()
        if not result:
            result = []
        return result

    @staticmethod
    def query_home_active_users(hours, params, refresh=False):
        """
        查询多少(24)小时内所有活跃用户
        """
        now = datetime.datetime.now()
        start_time = (now - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")

        if not refresh:
            result = cache.get(home_recommend_random_cache_key)
            if result:
                return result

        query = db.session.query(HomeRecommendModel).join(OpenLogModel, HomeRecommendModel.user_id == OpenLogModel.user_id)
        query = query.filter(or_(OpenLogModel.type == 4, OpenLogModel.type == 3, OpenLogModel.type == 2))
        query = query.filter(OpenLogModel.created_time >= start_time, OpenLogModel.created_time <= end_time)
        query = query.filter(HomeRecommendModel.status == 1, HomeRecommendModel.image_id != 0)
        query = query.filter(HomeRecommendModel.position == params.get("position", 2))
        result = query.filter(HomeRecommendModel.type_id == params.get("type_id", 1)).all()

        from random import shuffle
        shuffle(result)

        if result:
            cache.set(home_recommend_random_cache_key, result, home_recommend_top_cache_time)

        return result
