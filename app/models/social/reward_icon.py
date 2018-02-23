from app.models.base.base import BaseModel
from app import db, cache

reward_icon_cache_key = "RewardIcon:Type:"


class RewardIconModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "reward_icon"

    __fillable__ = ["id", "name", "price", "url", "type", "join"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), default="")
    price = db.Column(db.Integer, default=0)
    url = db.Column(db.String(100), default="")
    type = db.Column(db.Integer, default=1)
    join = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

    @staticmethod
    def query_icons_with_type(icon_type, refresh=False):
        cache_key = reward_icon_cache_key + str(icon_type)

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        result = RewardIconModel.query.filter_by(type=icon_type, status=1).all()
        if not result:
            result = []
        else:
            cache.set(cache_key, result)

        return result

    @staticmethod
    def query_icon_with_id(icon_id):
        return RewardIconModel.query.filter_by(id=icon_id).first()
