import datetime
from app.models.base.base import BaseModel
from app.models.account.user_info import UserInfoModel
from app.models.social.reward_icon import RewardIconModel
from app.models.social.offer_list import OfferListModel
from app.models.social.share_recommend import ShareRecommendModel
from app.models.commerce.order_info import OrderInfoModel
from app.models.commerce.order_meta import OrderMetaModel
from app.models.commerce.order_user_status import OrderUserStatusModel
from app.models.coffer.payment import PaymentModel
from app import db


class OfferModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "offer"

    offer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    present_id = db.Column(db.Integer, default=0)
    total_number = db.Column(db.Integer, default=0)
    join_number = db.Column(db.Integer, default=0)
    winner_user_id = db.Column(db.Integer, default=0)
    offer_status = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.datetime.now)
    due_time = db.Column(db.DateTime, default=datetime.datetime.now)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, params):
        if params:
            for key, value in params.items():
                if not hasattr(self, key):
                    continue

                setattr(self, key, value)
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def query_offer_model(share_id):
        return OfferModel.query.filter_by(share_id=share_id).first()

    @staticmethod
    def query_offer_mode_with_offer_id(offer_id):
        if not offer_id:
            return None
        return OfferModel.query.filter_by(offer_id=offer_id).first()

    @staticmethod
    def check_offer_publish(user_id):
        """
        检查用户当前是否可以发布悬赏
        :param user_id: 用户id
        :return: Bool
        """
        offer = OfferModel.query.filter_by(user_id=user_id, offer_status=2).filter(OfferModel.status != 0).first()
        if offer:
            return False
        return True

    @staticmethod
    def check_offer_enter_enable(offer_id, user_id):
        """
        检查当前是否还可以报名参加悬赏
        :param offer_id: 悬赏id
        :param user_id: 用户id
        """
        offer = OfferModel.query_offer_mode_with_offer_id(offer_id)
        if not offer:
            return False, "悬赏不存在"

        if offer.user_id == user_id:
            return False, "自己无法报名自己的悬赏"

        publish_user = UserInfoModel.query_user_model_by_id(offer.user_id)
        join_user = UserInfoModel.query_user_model_by_id(user_id)

        if publish_user.gender == join_user.gender:
            return False, "禁止同性报名"

        if OfferListModel.check_offer_enter_status(offer_id, user_id):
            return False, "您已经报名过此悬赏"

        if offer.offer_status == 1:
            return False, "悬赏尚未开始"
        elif offer.offer_status == 3:
            return False, "悬赏已经结束"
        elif offer.offer_status == 4:
            return False, "悬赏已被取消"
        elif offer.offer_status == 2:
            if offer.join_number >= offer.total_number:
                return False, "人数已满"
        return True, "可以报名"

    @staticmethod
    def format_offer_info(offer_model, share_model, login_user_id):
        if not offer_model:
            return dict()

        icon_info = RewardIconModel.query_icon_with_id(offer_model.present_id)

        if not share_model:
            from app.models.social.share import ShareModel
            share_model = ShareModel.query_share_model(offer_model.share_id)

        result = dict()

        result["present_url"] = icon_info.url if icon_info else ""
        result["price"] = share_model.price / 100
        result["total_number"] = offer_model.total_number
        result["join_number"] = offer_model.join_number
        result["status"] = offer_model.status
        result["offer_status"] = offer_model.offer_status
        result["limit_time"] = (offer_model.due_time - datetime.datetime.now()).seconds

        offer_enter = OfferListModel.check_offer_enter_status(offer_model.offer_id, login_user_id)
        result["enter_status"] = 1 if offer_enter else 0

        if offer_model.offer_status == 3:
            winner_info = UserInfoModel.query_user_model_by_id(offer_model.winner_user_id)
            result["winner"] = UserInfoModel.format_user_info(winner_info)
        elif offer_model.offer_status in [1, 2]:
            result["list"] = OfferListModel.query_offer_list(offer_model.offer_id)

        return result

    @staticmethod
    def choose_winner(offer_id, user_id):
        offer_info = OfferModel.query_offer_mode_with_offer_id(offer_id)
        if not offer_info:
            return False, "该悬赏不存在"

        # 更新悬赏信息
        offer_info.winner_user_id = user_id
        offer_info.offer_status = 3

        # 更新悬赏报名列表
        OfferListModel.choose_winner(offer_id, user_id)

        # 移除首页推荐
        ShareRecommendModel.remove_offer_from_recommend(offer_info.share_id)

        # 更新订单信息
        time_now = datetime.datetime.now()
        OrderInfoModel.update_order_info(offer_info.order_id, dict(ship_time=time_now,
                                                                   receive_time=time_now
                                                                   )
                                         )

        # 更新订单分表
        OrderMetaModel.update_order_meta(offer_info.order_id, dict(seller_id=user_id,
                                                                   order_status=6,
                                                                   ship_status=3)
                                         )

        PaymentModel.query.filter_by(order_id=offer_info.order_id, user_id=0).update(dict(user_id=user_id))

        # 新增用户订单关联
        OrderUserStatusModel(params={
            "user_id": user_id,
            "order_id": offer_info.order_id,
            "status": 1
        })

        db.session.commit()

        # TODO: 推送悬赏获胜消息
        return True, "Success"


