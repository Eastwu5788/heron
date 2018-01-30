from app import db
from app.models.social.album import AlbumModel
from app.models.account.user_info import UserInfoModel
from app.models.social.image import ImageModel


class ImageDataModel(object):

    @staticmethod
    def config_photo(params, image_model_list):

        album = AlbumModel.query_album_by_user_id(params["user_id"])
        user_info = UserInfoModel.query_user_model_by_id(params["user_id"])

        if not album:
            album = AlbumModel()
            album.user_id = params["user_id"]
            album.status = 1
            album.album_name = user_info.nickname + "的相册" if user_info else ""
            album.album_cover = ""

            db.session.add(album)
            db.session.commit()

        small_list = []
        big_list = []
        for image in image_model_list:
            image = image.get("image", None)
            if not image:
                continue

            image.album_id = album.id
            image.user_id = params["user_id"]

            small_list.append({
                "url": ImageModel.generate_image_url(image, 'b'),
                "width": 240,
                "height": 240,
                "image_id": image.image_id,
            })

            big_list.append({
                "url": ImageModel.generate_image_url(image, "f"),
                "width": 800,
                "height": 800,
                "image_id": image.image_id,
            })

            db.session.commit()

        return {"small": small_list, "big": big_list}
