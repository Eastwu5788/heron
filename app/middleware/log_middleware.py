import json
from flask import request

from .base_middleware import BaseMiddleWare
from config import initialize_logging
import logging

initialize_logging("request")

log = logging.getLogger("request")


class LogMiddleWare(BaseMiddleWare):

    @staticmethod
    def before_request():
        log_dict = {
            "url": request.url,
            "params": None,
            "method": request.method,
            "headers": dict(request.headers),
        }

        if request.method == "GET":
            log_dict["params"] = dict(request.values)
        else:
            log_dict["params"] = dict(request.form)
        log.info(json.dumps(log_dict))

