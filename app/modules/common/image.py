from . import common
from app.modules.base.base_handler import BaseHandler
from app.helper.response import *
from app.helper.upload import UploadImage


class ImageUploadHandler(BaseHandler):

    def post(self):
        img_upload = UploadImage()
        img_upload.save_images()
        print(img_upload.images)
        return json_success_response()


common.add_url_rule("/image/upload", view_func=ImageUploadHandler.as_view("upload"))
