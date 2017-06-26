from flask import Blueprint

person = Blueprint('personaluser', __name__)

from . import views
