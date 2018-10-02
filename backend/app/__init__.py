from flask import Flask, Blueprint

from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

from celery import Celery
import app.celeryconfig


socketio = SocketIO(message_queue='amqp://user:password@localhost//', managed_session=False)
jwt = JWTManager()

celery = Celery('newscenter', include=['app.tasks'])
celery.config_from_object(celeryconfig)


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'there is no secret'

    socketio.init_app(app)
    jwt.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
