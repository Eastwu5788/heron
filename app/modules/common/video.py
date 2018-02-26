from . import common
from app.modules.base.base_handler import BaseHandler

from app.helper.upload import UploadVideo
from app.helper.response import json_success_response


class VideoUploadHandler(BaseHandler):

    def post(self):
        uploader = UploadVideo()
        uploader.save_videos()
        return json_success_response({})


common.add_url_rule("/video/upload", view_func=VideoUploadHandler.as_view("video_upload"))