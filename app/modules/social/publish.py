from flask import g
from . import social
from app import db
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.helper.auth import login_required
from app.helper.response import *
from app.helper.upload import UploadImage
from app.helper.upload import UploadVideo

from app.modules.base.base_handler import BaseHandler

from app.models.social.share import ShareModel
from app.models.social.image import ImageModel
from app.models.social.social_meta import SocialMetaModel
from app.models.social.share_meta import ShareMetaModel
from app.models.social.share_recommend import ShareRecommendModel


class KindHandler(BaseHandler):

    def post(self):
        return json_fail_response(501)

    @login_required
    def get(self):
        result = [
            {
                "type": 2,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售照片",
            },
            {
                "type": 3,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售视频",
            },
            {
                "type": 4,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "出售微信",
            },
            {
                "type": 1,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "发布动态",
            },
            {
                "type": 5,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "发布悬赏",
            },
            {
                "type": 6,
                "img_url": "http://image.ahachat.cn/upload/material/shimizhaopian_tianjia@2x.png",
                "content": "邀请奖励",
            }
        ]
        return json_success_response(result)


class IndexHandler(BaseHandler):

    rule = {
        "content": Rule(allow_empty=True, default=""),
        "type": Rule(direct_type=int, enum=(10, 11, 20, 21, 30, 31, 70, 80, 90)),
        "position": Rule(allow_empty=True, default=""),
        "at_info": Rule(allow_empty=True, default=""),
        "price": Rule(direct_type=float, allow_empty=True, default=0)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        img_upload = UploadImage()
        video_upload = UploadVideo()

        if params["type"] == 10:
            if not img_upload.images:
                return json_fail_response(2201)
            img_upload.save_images()
        elif params["type"] == 30:
            if not video_upload.videos:
                return json_fail_response(2202)
            if not img_upload.images:
                return json_fail_response(2203)
            img_upload.save_images()
            video_upload.save_videos()

        share = ShareModel()
        share.content = params["content"]
        share.user_id = g.account["user_id"]
        share.type_id = params["type"]
        share.price = params["price"] * 100
        share.position = params["position"]
        # 默认需要进入审核状态
        share.status = 3
        share.data = params["at_info"]

        db.session.add(share)
        db.session.commit()

        # 更新图片数据
        if params["type"] == 10:
            self.update_image(img_upload.images, share)

        # 更新视频动态数据
        elif params["type"] == 30:
            img_model = img_upload.images[0]["image"]
            video_model = video_upload.videos[0]["video"]
            self.update_video(video_model, share, img_model)

        # 更新social_meta
        SocialMetaModel.update_social_meta_model(share.user_id, ["share"], meta_add=True)

        # 更新share_meta
        ShareMetaModel.update_share_meta_model(share.share_id, share.user_id)

        # 创建首页推荐数据
        ShareRecommendModel(share.share_id, share.user_id, position=2, status=2)

        share_info = ShareModel.format_share_model([share])

        return json_success_response(share_info)

    def update_image(self, images, share, img_type=10):
        for img in images:
            img_model = img["image"]
            img_model.share_id = share.share_id
            img_model.user_id = share.user_id
            img_model.type = img_type

        db.session.commit()

    def update_video(self, video_model, share_model, image_model):
        # 更新video表
        video_model.share_id = share_model.share_id
        video_model.user_id = share_model.user_id

        video_model.cover_id = image_model.image_id
        video_model.screenshot_a = image_model.image_a
        video_model.screenshot_b = image_model.image_b
        video_model.screenshot_c = image_model.image_c

        image_model.share_id = share_model.share_id
        image_model.user_id = share_model.user_id

        db.session.commit()


social.add_url_rule("/publish/kind", view_func=KindHandler.as_view("kind"))
social.add_url_rule("/publish/index", view_func=IndexHandler.as_view("index"))
