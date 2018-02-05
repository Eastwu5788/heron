from flask import Blueprint

social = Blueprint("social", __name__)

from . import publish
from . import share_recommend
from . import home_recommend
from . import share_list
from . import add_like
from . import share_detail
from . import like_list
from . import add_comment
from . import get_comment
from . import chat
from . import visitor
