from flask.views import MethodView
from app.helper.response import json_fail_response


class BaseHandler(MethodView):

    def get(self, *args):
        return json_fail_response(501)

    def post(self, *args):
        return json_fail_response(501)
