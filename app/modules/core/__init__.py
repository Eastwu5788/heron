from flask import Blueprint

core = Blueprint('core', __name__)

from . import app_version
from . import open_log
