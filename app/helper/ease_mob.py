from flask import current_app
from app import cache
import requests
import json
import logging
from config import initialize_logging

initialize_logging("mob")

ease_mob_token_cache_key = "EaseMobManager:Token:Cache:Key"

log = logging.getLogger("mob")


class EaseMobManager(object):

    request_header = {"Content-Type": "application/json"}
    ease_mob_base_url = "https://a1.easemob.com/"

    def __init__(self, client_id, client_secret, org_name, app_name):
        self.client_id = client_id
        self.client_secret = client_secret
        self.org_name = org_name
        self.app_name = app_name

    def generate_token_url(self):
        return self.ease_mob_base_url + self.org_name + "/" + self.app_name + "/token"

    def generate_user_url(self):
        return self.ease_mob_base_url + self.org_name + "/" + self.app_name + "/users"

    def request_access_token(self, use_cache=True):

        if use_cache:
            cache_token = cache.get(ease_mob_token_cache_key)
            if cache_token:
                return cache_token

        params = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        request = requests.post(self.generate_token_url(), headers=self.request_header, data=json.dumps(params))

        access_token = request.json().get("access_token", None)
        if access_token:
            cache.set(ease_mob_token_cache_key, access_token, 60*60*24)
        return access_token

    def register_new_user(self, ease_mob_id):
        access_token = self.request_access_token()
        access_token = "Bearer " + access_token

        header = dict({"Authorization": access_token}, **self.request_header)
        params = {"username": ease_mob_id, "password": ease_mob_id}
        request = requests.post(self.generate_user_url(), headers=header, data=json.dumps(params))

        log.info(json.dumps({
            "params": params,
            "token": access_token,
            "response": request.json(),
        }))

        if request.status_code == 200:
            return True
        else:
            return False


def mob_client():
    return EaseMobManager(client_id=current_app.config["MOB_CLIENT_ID"],
                          client_secret=current_app.config["MOB_CLIENT_SECRET"],
                          org_name=current_app.config["MOB_ORG_NAME"],
                          app_name=current_app.config["MOB_APP_NAME"])
