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
        # 查询首页顶部用户
        if params["position"] == 1:
            return self.home_top_user_request(params)

        # 查询首页下部推荐用户中的活跃用户
        active_user_list = []

        # 查询所有缓存的活跃用户
        if params["refresh"] == 0 and (params["last_id"] != 0 or params["offset"] != 0):
            cache_user_list = cache.get(self.home_active_user_cache_key)
            if cache_user_list:
                active_user_list = cache_user_list

        # 如果没有缓存的活跃用户，则查询数据库，并重新缓存结果
        if not active_user_list and params["refresh"] == 0:
            active_user_list = HomeRecommendModel.query_home_active_users(24, params)
            if active_user_list:
                cache.set(self.home_active_user_cache_key, active_user_list, self.home_active_user_cache_time)

        # 从缓存的活跃用户中分页获取要显示的用户列表
        offset = params["offset"]
        if offset == 0:
            result_list = active_user_list[params["last_id"]: offset+self.per_page]
            if not result_list:
                result_list = []
        else:
            result_list = []

        # 如果缓存用户不足一页，则从home_recommend表中随机查询其它的用户
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

        # 合并活跃用户和普通用户
        home_recommend = result_list + result_list_add

        if not home_recommend:
            return json_success_response([])

        return json_success_response(HomeRecommendHandler.format_home_users(home_recommend))

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
            item["cover"] = ImageModel.generate_image_url(image_model, "c") if image_model else ""
            item["last_id"] = 0
            item["offset"] = 0
            item["relation_type"] = 0

            result.append(item)

        return result


social.add_url_rule("/gethomerecommend/random", view_func=HomeRecommendHandler.as_view("recommend_random"))
