from flask import Blueprint

user = Blueprint("user", __name__)

from . import change_basic_info
from . import user_info
from . import user_basic_info
from . import follow_share_list
