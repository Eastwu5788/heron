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
from . import reward
from . import share_report
from . import offer
from . import driftingbottle
from . import image
from . import audio
from . import video

