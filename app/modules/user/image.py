from flask import g
from sqlalchemy import func
from . import user
from app import db
from app.modules.base.base_handler import BaseHandler

from app.models.account.user_info import UserInfoModel
from app.models.account.account_data import AccountDataModel
from app.models.social.image import ImageModel
from app.models.social.image_data import ImageDataModel
from app.models.social.social_meta import SocialMetaModel

from app.helper.upload import UploadImage
from app.helper.response import *
from app.helper.auth import login_required


album_max = 20


class UploadAvatarHandler(BaseHandler):

    @login_required
    def post(self):
        image_list = UploadImage()
        image_list.save_images()
        if not image_list.images:
            return json_fail_response(2401)

        image_model = image_list.images[0]["image"]

        user_info = UserInfoModel.query_user_model_by_id(g.account["user_id"], True)
        if not user_info:
            return json_fail_response(2101)

        # 缓存旧的头像
        old_avatar = user_info.avatar

        # 更新头像
        user_info.avatar = image_model.image_id

        # 头像绑定到图片模型
        image_model.user_id = user_info.user_id

        # 解绑旧的头像
        if old_avatar:
            ImageModel.query.filter_by(image_id=old_avatar).update(dict(user_id=0))

        db.session.commit()

        user_model = UserInfoModel.query_user_model_by_id(g.account["user_id"], True)
        AccountDataModel.query_request_account_by_token(g.account["access_token"], True)

        user_info = UserInfoModel.format_user_info(user_model)

        small_dict = {
            "url": user_info.get("avatar", ""),
            "width": 240,
            "height": 240,
        }
        big_dict = {
            "url": user_info.get("big_avatar", ""),
            "width": 800,
            "height": 800
        }

        result = {
            "small": small_dict,
            "big": big_dict
        }

        return json_success_response(result)


class UploadPhotoHandler(BaseHandler):

    @login_required
    def post(self):

        img_uploader = UploadImage()
        img_count = db.session.query(func.count(ImageModel.image_id)).filter_by(user_id=g.account["user_id"],
                                                                                status=1).filter(ImageModel.album_id != 0).scalar()
        photo_count = len(img_uploader.images) + img_count
        if photo_count > album_max:
            return json_fail_response(2404)

        img_uploader.save_images()

        result = ImageDataModel.config_photo({
            "user_id": g.account["user_id"]
        }, img_uploader.images)

        if result:
            SocialMetaModel.query.filter_by(user_id=g.account["user_id"]).update({
                "photo": photo_count
            })

        UserInfoModel.query_user_model_by_id(g.account["user_id"], True)
        return json_success_response(result)


user.add_url_rule("/image/uploadavatar", view_func=UploadAvatarHandler.as_view("image_upload_avatar"))
user.add_url_rule("/image/uploadphoto", view_func=UploadPhotoHandler.as_view("image_upload_photo"))
