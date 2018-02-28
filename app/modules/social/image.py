from . import social
from app.modules.base.base_handler import BaseHandler
from app.models.social.image import ImageModel
from app.helper.auth import login_required
from app.helper.upload import UploadImage
from app.helper.response import json_success_response


class UploadChatImageHandler(BaseHandler):

    @login_required
    def post(self):
        image_uploader = UploadImage()
        image_uploader.save_images()

        result = list()

        for image_dict in image_uploader.images:
            image_model = image_dict.get("image", None)
            if not image_model:
                continue

            image_dict = image_model.format_model(attr_list=["image_id", "image_width", "image_height"])
            image_dict["image_url"] = ImageModel.generate_image_url(image_model)
            image_dict["tiny_img"] = ImageModel.generate_image_url(image_model, 'e')

            result.append(image_dict)

        return json_success_response(result[0])


social.add_url_rule("/image/uploadchatimage", view_func=UploadChatImageHandler.as_view("image_upload_chat_image"))

