import datetime
from app import db, cache
from app.models.base.base import BaseModel

video_meta_cache_key = "VideoMetaModel:Query:VideoID:"
video_meta_cache_time = 60 * 60 * 24


class VideoMetaModel(BaseModel, db.Model):

    __bind_key__ = "a_social"
    __tablename__ = "video_meta"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, default=0)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_video_meta(video_id, refresh=False):
        if not video_id:
            return None

        cache_key = video_meta_cache_key + str(video_id)
        if not refresh:
            cache_result = cache.get(cache_key)
            if cache_result:
                return cache_result

        db_result = VideoMetaModel.query.filter_by(video_id=video_id).first()
        if db_result:
            cache.set(cache_key, db_result, video_meta_cache_time)

        return db_result

    @staticmethod
    def query_video_meta_list(video_id_list):
        if not video_id_list:
            return []

        result = VideoMetaModel.query.filter(VideoMetaModel.video_id.in_(video_id_list)).all()
        if not result:
            return []
        return result

