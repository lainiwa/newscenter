from flask import Blueprint

main = Blueprint('main', __name__, static_folder='../../../frontend/dist', static_url_path='')

from . import routes #, events