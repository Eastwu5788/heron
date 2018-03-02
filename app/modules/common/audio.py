from . import common
from app.modules.base.base_handler import BaseHandler
from app.helper.response import *
from app.helper.upload import UploadAudio


class AudioUploadHandler(BaseHandler):

    def post(self):
        audio_upload = UploadAudio()
        audio_upload.save_audios()
        return json_success_response()



common.add_url_rule("/audio/upload", view_func=AudioUploadHandler.as_view("audio_upload"))
