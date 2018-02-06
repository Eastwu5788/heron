import datetime
from app.models.base.base import BaseModel
from app import db, cache

from app.models.commerce.order_image import OrderImageModel
from app.helper.utils import array_column, array_column_index

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
    def query_image_by_image_id_list(image_id_list=list()):
        if not image_id_list:
            return []

        result = ImageModel.query.filter(ImageModel.image_id.in_(image_id_list)).all()
        if not result:
            result = []

        return result

    @staticmethod
    def query_share_images(share_id):
        if not share_id:
            return []

        model_list = ImageModel.query.filter_by(share_id=share_id, status=1).order_by(ImageModel.image_id.asc()).all()
        if not model_list:
            model_list = []
        return model_list

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
    def query_album_image_list(user_id, album_id):
        query = ImageModel.query.filter_by(user_id=user_id, album_id=album_id, status=1)
        image_model_list = query.order_by(ImageModel.image_id.desc()).all()
        if not image_model_list:
            image_model_list = []
        return image_model_list

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
    def query_private_image(user_id, visitor_id=0, last_id=0, limit=15):
        """
        查询某个用户的私密照片
        :param user_id: 查询的用户id
        :param visitor_id: 访问者id
        :param last_id: 最后一张照片id
        :param limit: 分页
        """
        if not user_id or not visitor_id:
            return []

        query = ImageModel.query.filter_by(user_id=user_id, type=11, status=1)
        if last_id:
            query = query.filter(ImageModel.image_id < last_id)

        result = query.order_by(ImageModel.image_id.desc()).limit(limit).all()
        if not result:
            result = []

        return ImageModel.format_private_image_model(result, user_id, visitor_id)

    @staticmethod
    def query_random_private_image(user_id, visitor_id, last_id=0, offset=0, limit=15):
        invalid_order_list = OrderImageModel.query_invalid_order_list(user_id, visitor_id)
        invalid_image_id_list = array_column(invalid_order_list, "image_id")

        random_result_list = ImageModel.query_random_list(user_id, last_id, offset, limit, invalid_image_id_list)
        if len(random_result_list) == limit:
            return ImageModel.format_private_image_model(random_result_list, user_id, visitor_id)

        if last_id > offset or last_id == 0:
            last_id = 0.5
            limit = limit - len(random_result_list)
        else:
            return ImageModel.format_private_image_model(random_result_list, user_id, visitor_id)

        merge_result_list = ImageModel.query_random_list(user_id, last_id, offset, limit, invalid_image_id_list)
        random_result_list += merge_result_list

        return ImageModel.format_private_image_model(random_result_list, user_id, visitor_id)

    @staticmethod
    def query_random_list(user_id, last_id, offset, limit, invalid_image_ids):
        query = ImageModel.query.filter_by(user_id=user_id, type=11, status=1)

        if offset:
            if last_id == 0:
                query = query.filter(ImageModel.image_id > offset)
            elif last_id > offset:
                query = query.filter(ImageModel.image_id > last_id)
            else:
                query = query.filter(ImageModel.image_id > last_id, ImageModel.image_id <= offset)

        if invalid_image_ids:
            query = query.filter(ImageModel.image_id.notin_(invalid_image_ids))

        result = query.order_by(ImageModel.image_id.asc()).limit(limit).all()
        if not result:
            result = []
        return result

    @staticmethod
    def format_private_image_model(img_model_list=list(), user_id=0, visitor_id=0):
        if not img_model_list or not user_id or not visitor_id:
            return []

        pay_image_id_list = []

        if user_id != visitor_id:
            img_id_list = array_column(img_model_list, "image_id")
            query = OrderImageModel.query.with_entities(OrderImageModel.image_id).filter_by(buyer_id=visitor_id, status=2)
            order_image_list = query.filter(OrderImageModel.image_id.in_(img_id_list)).all()
            pay_image_id_list = array_column_index(order_image_list, 0)

        result = list()
        for image_model in img_model_list:
            pay = 1 if user_id == visitor_id or image_model.image_id in pay_image_id_list else 0

            small = big = dict()
            small["width"] = big["width"] = image_model.image_width
            small["height"] = big["height"] = image_model.image_height
            small["image_id"] = big["image_id"] = image_model.image_id
            small["url"] = ImageModel.generate_image_url(image_model, "b" if pay else "x")
            big["url"] = ImageModel.generate_image_url(image_model, "f" if pay else "x")

            item = dict()
            item["pay"] = pay
            item["price"] = 14
            item["small"] = small
            item["big"] = big
            item["download"] = ImageModel.generate_image_url(image_model, "g" if pay else "x")
            result.append(item)

        return result

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
