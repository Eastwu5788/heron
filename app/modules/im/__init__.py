from flask import Blueprint

im = Blueprint("im", __name__)

from . import immsg
