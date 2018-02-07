from flask import Blueprint

user = Blueprint("user", __name__)

from . import change_basic_info
from . import user_info
from . import user_basic_info
from . import follow_share_list
from . import add_follow
from . import friends
from . import image
from . import invite
from . import aha_account
from . import user_feed_back
from . import wechat
from . import user_black
from . import privatelibrary
from . import add_update_user_black
