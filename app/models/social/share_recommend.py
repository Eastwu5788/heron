import datetime
from sqlalchemy import or_, and_
from app.models.base.base import BaseModel
from app import db


class ShareRecommendModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "share_recommend"

    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.Integer, default=0)
    share_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    share_type = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, share_id, user_id, position, status):
        """
        构造方法
        :param share_id: 动态id
        :param user_id: 用户id
        :param position: 位置
        :param status: 状态
        """
        self.share_id = share_id
        self.user_id = user_id
        self.position = position
        self.status = status

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def query_share_recommend_id_list(position=0, user_id=0, last_share_id=0):
        """
        查询动态推荐的内容
        :param position: 推荐的位置
        :param user_id: 访问者id
        :param last_share_id: 最后一条动态id
        """
        query = ShareRecommendModel.query.with_entities(ShareRecommendModel.share_id).filter(
            or_(
              and_(ShareRecommendModel.status == 1),
              and_(ShareRecommendModel.status == 3, ShareRecommendModel.user_id == user_id)
            ),
            ShareRecommendModel.position == position,
        )

        if last_share_id:
            last_model = ShareRecommendModel.query.filter_by(share_id=last_share_id).first()
            if last_model:
                query = query.filter(ShareRecommendModel.id < last_model.id)

        result = query.order_by(ShareRecommendModel.id.desc()).all()

        result_list = []
        for arr in result:
            if not arr:
                continue
            result_list.append(arr[0])

        return result_list

    @staticmethod
    def remove_offer_from_recommend(share_id):
        """
        将悬赏从首页推荐列表中删除
        :param share_id:
        """
        if not share_id:
            return False

        ShareRecommendModel.query.filter_by(share_id=share_id).update(dict(share_type=0, status=0))

