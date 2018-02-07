import datetime
from sqlalchemy import and_, or_
from sqlalchemy.sql import func
from app.models.base.base import BaseModel

from app.helper.utils import array_column

from app import db


class UserConsumerModel(db.Model, BaseModel):
    __bind_key__ = "a_social"
    __tablename__ = "user_consumer"

    id = db.Column(db.Integer, primary_key=True)
    consumer_user_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    money = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_trade_relationship(user_id, user_id_list):
        """
        查询用户user_id与其它用户是否有交易关系
        :param user_id: 要查询的用户id
        :param user_id_list: 其它用户
        :return:
        """
        if not isinstance(user_id_list, list):
            query = UserConsumerModel.query.filter_by(status=1).filter(
                or_(
                    and_(
                        UserConsumerModel.consumer_user_id == user_id,
                        UserConsumerModel.user_id == user_id_list,
                    ),
                    and_(
                        UserConsumerModel.user_id == user_id,
                        UserConsumerModel.consumer_user_id == user_id_list
                    )
                )
            ).first()
            if query:
                return 1
            return 0
        else:
            query = UserConsumerModel.query.filter_by(status=1).filter(
                or_(
                    and_(
                        UserConsumerModel.consumer_user_id == user_id,
                        UserConsumerModel.user_id.in_(user_id_list)
                    ),
                    and_(
                        UserConsumerModel.consumer_user_id.in_(user_id_list),
                        UserConsumerModel.user_id == user_id
                    )
                )
            ).all()

            if not query:
                return []

            user_id_list_1 = array_column(query, "user_id")
            user_id_list_2 = array_column(query, "consumer_user_id")

            return list(set(user_id_list_1).union(set(user_id_list_2)))

    @staticmethod
    def query_relation_consumer_money(user_id, other_user_id):
        """
        查询对方为我消费的总金额
        :param user_id: 我的id
        :param other_user_id: 对方的id
        """
        query = db.session.query(func.sum(UserConsumerModel.money))
        result = query.filter_by(user_id=user_id, consumer_user_id=other_user_id, status=1).all()
        if not result:
            result = 0
        return result[0][0]
