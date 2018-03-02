from . import social
from app.modules.base.base_handler import BaseHandler

from app.models.social.audio import AudioModel

from app.helper.upload import UploadAudio
from app.helper.auth import login_required
from app.helper.response import *


class UploadChatAudioHandler(BaseHandler):

    @login_required
    def post(self):
        audio_upload = UploadAudio()
        if not audio_upload.audios:
            return json_fail_response(2204)

        audio_upload.save_audios()
        result = AudioModel.format_audio_model(audio_upload.audios[0].get("audio", None))
        return json_success_response(result)


social.add_url_rule("/audio/uploadchataudio", view_func=UploadChatAudioHandler.as_view("audio_upload_chat_audio"))
