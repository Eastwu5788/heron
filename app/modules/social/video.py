from . import social
from app import db
from app.modules.base.base_handler import BaseHandler
from app.models.social.image import ImageModel
from app.models.social.video import VideoModel
from app.helper.auth import login_required
from app.helper.upload import UploadImage, UploadVideo
from app.helper.response import json_success_response, json_fail_response


class UploadChatVideoHandler(BaseHandler):

    @login_required
    def post(self):
        upload_video = UploadVideo()
        upload_image = UploadImage()

        if not upload_video.videos:
            return json_fail_response(2202)
        if not upload_image.images:
            return json_fail_response(2203)

        upload_video.save_videos()
        upload_image.save_images()

        img_model = upload_image.images[0]["image"]
        video_model = upload_video.videos[0]["video"]

        video_model.cover_id = img_model.image_id
        db.session.commit()

        video_info = VideoModel.format_video_info(video_model)
        video_info["video_id"] = video_model.video_id
        video_info["tiny_img"] = ImageModel.generate_image_url(img_model, "e")

        return json_success_response(video_info)


social.add_url_rule("/video/uploadchatvideo", view_func=UploadChatVideoHandler.as_view("video_upload_chat_video"))
