from flask import Blueprint

passport = Blueprint('passport', __name__)

from . import login
from . import login_mobile
from . import register_mobile
from . import logout
