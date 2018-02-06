from flask import g
from sqlalchemy import func
from app import redis, db
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.modules.base.base_handler import BaseHandler

from app.helper.response import *
from app.helper.auth import login_required
from app.helper.upload import UploadImage

from app.models.account.user_info import UserInfoModel
from app.models.account.user_invite_code import UserInviteCodeModel
from app.models.account.user_wechat import UserWeChatModel
from app.models.account.user_id_relation import UserIdRelationModel
from app.models.account.remark_name import RemarkNameModel
from app.models.social.user_consumer import UserConsumerModel
from app.models.social.social_page import SocialPageModel
from app.models.coffer.user_profit import UserProfitModel
from app.models.account.user_location import UserLocationModel
from app.models.account.aha_account import AhaAccountModel
from app.models.social.share import ShareModel
from app.models.core.open_log import OpenLogModel
from app.models.social.visitor_record import VisitorRecordModel
from app.models.base.redis import RedisModel
from app.models.social.follow import FollowModel
from app.models.social.image import ImageModel
from app.models.commerce.order_meta import OrderMetaModel
from app.models.social.wechat_want_buy import WeChatWantBuyModel
from app.models.social.social_meta import SocialMetaModel
from . import user


user_invite_url = 'http://w.ahachat.cn/invite/invite/person?from=singlemessage&isappinstalled=1&code='


class MeHandler(BaseHandler):

    @login_required
    def get(self, *args):
        user_id = g.account["user_id"]

        user_info = UserInfoModel.query_user_model_by_id(user_id)
        if not user_info:
            return json_success_response({})

        result = dict()

        result["user_info"] = UserInfoModel.format_user_info(user_info)
        result["profit_today"] = 0
        result["ok_percent"] = UserInfoModel.calculate_ok_percent(user_id)

        invite_code = UserInviteCodeModel.query_user_invite_code(user_id)
        result["invite_url"] = user_invite_url + invite_code

        result["new_visitor"] = RedisModel.query_new_message(user_id, RedisModel.new_visitor)
        result["follow_add"] = 0

        social_meta = SocialMetaModel.query_social_meta_info(g.account["user_id"])
        result["wechat_info"] = MeHandler.format_wechat_info(g.account["user_id"],
                                                             social_meta.wechat_want if social_meta else 0
                                                             )
        return json_success_response(result)

    @staticmethod
    def format_wechat_info(user_id, wechat_want_buy=0):
        result = {
            "wechat_status": 0,
            "wechat_price": 0,
            "wechat": "",
            "wechat_buy_status": 0,
            "wechat_sell_num": 0,
            "wechat_added": 0,
            "wechat_want_buy": 0,
            "wechat_want_buy_status": 0,
        }

        wechat = UserWeChatModel.query_user_wechat_model(user_id)
        if wechat:
            result["wechat_status"] = wechat.status
            result["wechat_price"] = wechat.price / 100
        else:
            result["wechat_status"] = 2

        wechat_buy = MeHandler.check_buy_wechat(user_id)
        result["wechat_buy_status"] = wechat_buy.get("wechat_buy_status", 0)
        result["wechat_sell_num"] = wechat_buy.get("wechat_sell_num", 0)
        result["wechat_added"] = wechat_buy.get("wechat_added", 0)
        result["wechat_want_buy"] = wechat_want_buy

        want_buy_model = WeChatWantBuyModel.query_wechat_want_buy(user_id, g.account["user_id"])
        result["wechat_want_buy_status"] = 1 if want_buy_model else 0

        return result

    @staticmethod
    def check_buy_wechat(user_id):
        query = OrderMetaModel.query.filter_by(seller_id=user_id, product_type=80, pay_status=1)
        sell_num = query.count()
        order_meta = query.filter_by(buyer_id=g.account["user_id"]).first()

        result = {
            "wechat_buy_status": 1 if order_meta else 0,
            "wechat_sell_num": sell_num,
            "wechat_added": 0,
        }

        if order_meta and order_meta.ship_status == 3:
            result["wechat_added"] = 1

        return result


class IndexHandler(BaseHandler):

    rule = {
        "user_id": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):

        if params["user_id"] == 0:
            return json_fail_response(2101)

        user_info = UserInfoModel.query_user_model_by_id(params["user_id"])
        result = UserInfoModel.format_user_info(user_info)

        social_meta_info = SocialMetaModel.query_social_meta_info(params["user_id"])
        result["share_num"] = social_meta_info.share if social_meta_info else 0
        result["follow_num"] = social_meta_info.following if social_meta_info else 0
        result["fans_num"] = social_meta_info.follower if social_meta_info else 0
        result["follow_status"] = FollowModel.query_relation_to_user(g.account["user_id"], params["user_id"])
        result["album"] = UserInfoModel.query_user_album(params["user_id"])

        social_page_info = SocialPageModel.query_social_page_model(params["user_id"])
        result["user_banner"] = social_page_info.get("cover", "")
        result["user_banner_type"] = social_page_info.get("cover_type", 1)

        if result["user_banner_type"] == 2:
            result["orientation"] = ""
            result["user_banner_cover"] = ""

        if params["user_id"] == g.account["user_id"]:
            result["profit"] = IndexHandler.query_user_profit(params["user_id"])

        if result["identified"] == 1:
            result["identify_title"] = "官方认证：" + result["identify_title"]

        result["wechat_info"] = MeHandler.format_wechat_info(params["user_id"],
                                                             social_meta_info.wechat_want if social_meta_info else 0
                                                             )

        user_location = UserLocationModel.query.filter(UserLocationModel.id == user_info.location_id).first()
        result["latitude"] = user_location.latitude if user_location else 0
        result["longitude"] = user_location.longitude if user_location else 0

        result["changeable_aha"] = 1
        result["aha_id"] = ''

        aha_info = AhaAccountModel.query_aha_account_by_id(params['user_id'], auto_formated=False)
        if aha_info:
            result["changeable_aha"] = aha_info.changeable_aha
            if aha_info.changeable_aha == 0:
                result["aha_id"] = aha_info.aha_id

        # 最近的动态
        result["share_info"] = ShareModel.query_recent_share_photo(params['user_id'], g.account["user_id"])
        # 是否有交易记录
        result["had_trade"] = 1
        # 备注昵称
        result["remark_name"] = ""

        last_login = OpenLogModel.query_last_login(params["user_id"])
        result["last_login"] = 0
        if last_login:
            result["last_login"] = time.time() - time.mktime(last_login.created_time.timetuple())

        # 插入访客记录
        if g.account["user_id"] != 0 and g.account["user_id"] != params["user_id"]:
            RedisModel.add_new_message(params["user_id"], RedisModel.new_visitor)
            VisitorRecordModel(user_id=params["user_id"], visitor_user_id=g.account["user_id"])

        return json_success_response(result)

    @staticmethod
    def query_user_profit(user_id):
        user_profit = UserProfitModel.query_user_profit(user_id)

        result = {
            "all_money": user_profit.money if user_profit else 0,
            "today_money": user_profit.today_money if user_profit else 0,
        }
        return result


class ChangeCoverHandler(BaseHandler):

    rule = {
        "cover_type": Rule(direct_type=int)
    }

    @login_required
    @filter_params(post=rule)
    def post(self, params):
        img_upload = UploadImage()
        print(params)
        if params["cover_type"] == 1:
            if not img_upload.images:
                return json_fail_response(2402)

            img_upload.save_images()
            image_model = img_upload.images[0]["image"]
            ChangeCoverHandler.change_cover_image(image_model)
        else:
            pass

        cover_info = SocialPageModel.query_social_page_model(g.account["user_id"])
        result = {"user_banner": cover_info.get("cover", ""), "user_banner_type": cover_info.get("cover_type", 0)}
        if result.get("user_banner_type", 0) == 2:
            result["orientation"] = cover_info.get("orientation")
            result["user_banner_cover"] = cover_info.get("video_img", "")

        UserInfoModel.query_user_model_by_id(g.account["user_id"], True)
        return json_success_response(result)

    @staticmethod
    def change_cover_image(image_model):
        """
        修改封面图片
        """
        image_model.user_id = g.account["user_id"]

        UserInfoModel.query.filter_by(user_id=g.account["user_id"], status=1).update({
            "cover": image_model.image_id,
            "cover_type": 1,
        })

        social_page = SocialPageModel.query_social_page_model(g.account["user_id"], auto_format=False)
        if not social_page:
            social_page = SocialPageModel()
            social_page.user_id = g.account["user_id"]
            social_page.cover = image_model.image_id
            social_page.cover_type = 1

            db.session.add(social_page)
        else:
            social_page.cover = image_model.image_id
            social_page.cover_type = 1

        db.session.commit()

    @staticmethod
    def change_cover_video(params):
        pass


class EaseMobHandler(BaseHandler):

    rule = {
        "huanxin_uid": Rule()
    }

    @login_required
    @filter_params(get=rule)
    def get(self, params):
        user_id_relation = UserIdRelationModel.query_user_by_ease_mob_id(params["huanxin_uid"])
        if not user_id_relation:
            return json_fail_response(2109)

        user_info = UserInfoModel.query_user_model_by_id(user_id_relation.user_id)
        has_trade = UserConsumerModel.query_trade_relationship(user_id_relation.user_id, g.account["user_id"])
        follow_status = FollowModel.query_relation_to_user(g.account["user_id"], user_id_relation.user_id)
        remark_name = RemarkNameModel.query_remark_name(g.account["user_id"], user_id_relation.user_id)

        result = {
            "user_info": UserInfoModel.format_user_info(user_info),
            "had_trade": has_trade,
            "follow_status": follow_status,
            "black_status": 0,
            "remark_name": remark_name.remark_nickname if remark_name else ""
        }
        return json_success_response(result)


user.add_url_rule("/userinfo/me", view_func=MeHandler.as_view("user_info_me"))
user.add_url_rule("/userinfo/index", view_func=IndexHandler.as_view("user_info_index"))
user.add_url_rule("/userinfo/changecover", view_func=ChangeCoverHandler.as_view("user_info_change_cover"))
user.add_url_rule("/userinfo/getbyhuanxin", view_func=EaseMobHandler.as_view("ease_mob_user_info"))
