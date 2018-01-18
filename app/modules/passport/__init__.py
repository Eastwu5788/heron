from flask import Blueprint

passport = Blueprint('passport', __name__)

from . import login
