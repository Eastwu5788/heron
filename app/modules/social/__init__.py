from flask import Blueprint

social = Blueprint("social", __name__)

from . import publish
