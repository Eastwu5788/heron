from flask import Blueprint

user = Blueprint("user", __name__)

from . import change_basic_info
