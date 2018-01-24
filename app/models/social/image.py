import datetime
from app.models.base.base import BaseModel
from app import db, cache

cache_image_id_key = "Social:ImageModel:Query:ID:"
cache_image_id_time = 60*60*24


class ImageModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "image"

    image_id = db.Column(db.Integer, primary_key=True)

    share_id = db.Column(db.Integer, default=0)
    album_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)

    type = db.Column(db.Integer, default=0)
    image_o = db.Column(db.String(100), default="")
    image_a = db.Column(db.String(100), default="")
    image_b = db.Column(db.String(100), default="")
    image_c = db.Column(db.String(100), default="")
    image_d = db.Column(db.String(100), default="")
    image_e = db.Column(db.String(100), default="")
    image_f = db.Column(db.String(100), default="")
    image_g = db.Column(db.String(100), default="")
    image_x = db.Column(db.String(100), default="")

    image_width = db.Column(db.Integer, default=0)
    image_height = db.Column(db.Integer, default=0)

    file_name = db.Column(db.String(32), default="")
    file_ext = db.Column(db.String(10), default="")
    mime_type = db.Column(db.String(20), default="")
    file_size = db.Column(db.Integer(), default=0)
    hash_key = db.Column(db.String(32), default="")

    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_share_image_list(share_id_list):
        query = ImageModel.query.filter_by(status=1).filter(ImageModel.share_id.in_(share_id_list))
        image_model_list = query.order_by(ImageModel.image_id.asc()).all()

        result = dict()

        for image_model in image_model_list:
            ori_arr = result.get(image_model.share_id, None)
            if not ori_arr:
                ori_arr = [image_model]
                result[image_model.share_id] = ori_arr
            else:
                ori_arr.append(image_model)
        return result

    @staticmethod
    def query_image_by_id(img_id, refresh=False):
        cache_key = cache_image_id_key + str(img_id)

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        model = ImageModel.query.filter_by(image_id=img_id, status=1).first()
        if model:
            cache.set(cache_key, model, cache_image_id_time)

        return model

    @staticmethod
    def format_image_model(img_model_list=list(), size='o'):
        result = list()

        if not img_model_list:
            return result

        for item in img_model_list:
            item_dic = {
                "width": item.image_width,
                "height": item.image_height,
                "url": ImageModel.generate_image_url(item, size=size)
            }
            result.append(item_dic)

        return result

    @staticmethod
    def generate_image_url(img_model, size='o'):
        from heron import app
        url = app.config["IMAGE_HOST"]

        attr = "image_" + size
        if hasattr(img_model, attr):
            url += getattr(img_model, attr)

        return url
