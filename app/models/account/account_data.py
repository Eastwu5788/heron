from app.models.base.base import BaseModel
from app.models.account.user_access_token import UserAccessTokenModel
from app.models.account.user_account import UserAccountModel
from app.models.account.user_info import UserInfoModel

account_data_cache_key = "AccountDataModel:Initialize:Token:"


class AccountDataModel(BaseModel):

    @staticmethod
    def query_request_account_by_token(token, refresh=False):
        """
        通过用户的token交换到用户信息
        :param token: 用户的token
        :param refresh: 是否使用缓存中的数据
        """
        from app import cache
        cache_key = account_data_cache_key + token

        if not refresh:
            result = cache.get(cache_key)
            if result:
                return result

        account_dict = dict()
        # 1. 用户access_token信息
        access_token = UserAccessTokenModel.query_useful_access_token(token, refresh)
        user_id = 0

        if access_token:
            user_id = access_token.user_id
            account_dict = dict(access_token.to_dict(filter_params=True), **account_dict)

        account = UserAccountModel.query_account_by_user_id(user_id)
        if account:
            account_dict = dict(account.to_dict(filter_params=True), **account_dict)

        user_info = UserInfoModel.query_user_model_by_id(user_id, refresh=refresh)
        if user_info:
            account_dict = dict(user_info.to_dict(filter_params=True), **account_dict)

        cache.set(cache_key, account_dict)
        return account_dict
