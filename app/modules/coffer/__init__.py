from flask import Blueprint

coffer = Blueprint('coffer', __name__)

from . import order
