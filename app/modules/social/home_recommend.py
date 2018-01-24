from random import shuffle, randint
from flask import g
from sqlalchemy import func
from . import social
from app import db, cache
from app.modules.base.base_handler import BaseHandler
from app.modules.vendor.pre_request.flask import filter_params
from app.modules.vendor.pre_request.filter_rules import Rule

from app.models.social.home_recommend import HomeRecommendModel
from app.models.social.image import ImageModel
from app.models.account.user_info import UserInfoModel
from app.helper.response import *
from app.helper.utils import array_column_key, array_column

class HomeRecommendHandler(BaseHandler):

    home_top_page_count = 20

    home_active_user_cache_key = "Social:GetHomeRecommend:Random:"
    home_active_user_cache_time = 60 * 60

    per_page = 10

    rule = {
        "position": Rule(direct_type=int, enum=[1, 2]),
        "type_id": Rule(direct_type=int, enum=[1, 2, 3, 4]),
        "last_id": Rule(direct_type=int, allow_empty=True, default=0),
        "offset": Rule(direct_type=int, allow_empty=True, default=0),
        "refresh": Rule(direct_type=int, allow_empty=True, default=0)
    }

    @filter_params(get=rule)
    def get(self, params):
        user_id = g.account["user_id"]

        if params["position"] == 1:
            return self.home_top_user_request(params)

        active_user_list = []
        # 加载更多时，先读取缓存中的活跃用户
        if params["refresh"] == 0 and (params["last_id"] != 0 or params["offset"] != 0):
            cache_user_list = cache.get(self.home_active_user_cache_key)
            if cache_user_list:
                active_user_list = cache_user_list

        if not active_user_list and params["refresh"] == 0:
            active_user_list = HomeRecommendModel.query_home_active_users(24, params)
            if active_user_list:
                cache.set(self.home_active_user_cache_key, active_user_list, self.home_active_user_cache_time)

        offset = params["offset"]
        if offset == 0:
            result_list = active_user_list[params["last_id"]: offset+self.per_page]
        else:
            result_list = []

        if result_list and len(result_list) < self.per_page:
            params["active_ids"] = array_column(result_list, "user_id")

        params["limit"] = self.per_page - len(result_list)
        if params["limit"] > 0:
            params["active_list"] = array_column(active_user_list, "user_id")

            if not params["offset"]:
                db_count = db.session.query(func.count(HomeRecommendModel.id)).scalar()
                params["offset"] = randint(1, db_count)
                params["last_id"] = 0

            result_list_add = HomeRecommendModel.query_home_random_users(params)
        else:
            result_list_add = []

        home_recommend = result_list_add + result_list
        if not home_recommend:
            return json_success_response([])

        return json_success_response([])



    def home_top_user_request(self, params):
        # 查询首页推荐的所有用户
        top_users = HomeRecommendModel.query_home_top_users()
        # 乱序，产生随机效果
        shuffle(top_users)
        # 首页最多20人
        if len(top_users) > self.home_top_page_count:
            top_users = top_users[:self.home_top_page_count]
        # 标准格式化数据
        result = HomeRecommendHandler.format_home_users(top_users)
        # 返回结果
        return json_success_response(result)

    @staticmethod
    def format_home_users(user_list=list()):
        """
        格式化首页的用户
        """
        result = []

        if not user_list:
            return result

        image_list = ImageModel.query_image_by_image_id_list(array_column(user_list, "image_id"))
        image_list = array_column_key(image_list, "user_id")

        for user in user_list:

            item = dict()

            # 用户信息
            user_info = UserInfoModel.query_user_model_by_id(user.user_id)
            item["user_info"] = UserInfoModel.format_user_info(user_info)

            image_model = image_list.get(user.user_id, None)
            item["cover"] = ImageModel.format_image_model(image_model, "c") if image_model else ""
            item["last_id"] = 0
            item["offset"] = 0
            item["relation_type"] = 0

            result.append(item)

        return result


social.add_url_rule("/social/gethomerecommend/random", view_func=HomeRecommendHandler.as_view("recommend_random"))
