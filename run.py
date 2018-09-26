import os
import tempfile
from time import sleep
from celery import Celery
from PIL import Image

import flask
from flask import Flask, request, abort, redirect, url_for, send_file
from flask_restful import Api, Resource, reqparse
from werkzeug import secure_filename
from flask_socketio import SocketIO, emit, join_room, rooms

import celeryconfig


app = Flask(__name__, static_folder='dist', static_url_path='')
app.config['SECRET_KEY'] = 'there is no secret'
# app.config.from_pyfile('configs/flask.py')
# app.config.from_pyfile('config_file.cfg')

socketio = SocketIO(app, message_queue='amqp://user:password@localhost//')

celery = Celery('newscenter')
celery.config_from_object(celeryconfig)


@celery.task(name='resize_image')  # WTF?! lse name='proj.resize_image' works from ipython, but not from here
def resize_image(path_orig, path_resized, sizes, keep_aspect_ratio=True, remove_orig=False):
    """Optimize image size.

    Args:
        path_orig (str): path to original image file (can also be `io.BufferedRandom` type of stream)
        path_resized (str): path to optimized image to be created at
        sizes (tuple): a (width, height) of the optimized image
        keep_aspect_ratio (bool): if set, fit image into `sizes`, but preserve it's aspect ratio
    """
    sleep(2)
    img = Image.open(path_orig).convert('RGB')
    if keep_aspect_ratio:
        img.thumbnail(sizes, Image.ANTIALIAS)
    else:
        img = img.resize(sizes, Image.ANTIALIAS)
    img.save(path_resized, 'JPEG', optimize=True)  # WTF?! quality=80 makes it worse
    if remove_orig:
        os.remove(path_orig)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # print(flask.request.files)
    # print(flask.request.files.getlist('file[]'))
    uploaded_files = flask.request.files.getlist('file[]')
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        # file.save(os.path.join('uploads', filename))
        # Image.open(file.stream).save('uploads/_' + filename, 'JPEG', optimize=True)
        fd, path = tempfile.mkstemp()
        # print(path)
        Image.open(file.stream).save(path, 'JPEG', optimize=True)
        resize_image.delay(path, 'uploads/_' + filename, (300, 300), False)
        # resize_image.delay(file.stream, 'uploads/_' + filename, (150, 150), False)
    # print(uploaded_files)
    return ''


@socketio.on('connection', namespace='/test')
def confirmation_message(message):
    print(message)
    emit('confirmation', {'connection_confirmation': message['connection_confirmation']})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9998)


# from funcy import walk_values, iffy, caller, omit
# from sqlalchemy import create_engine, Column, String, ForeignKey, DateTime, Integer, FetchedValue, text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import JSON
# from sqlalchemy.ext.declarative import declared_attr
# from sqlalchemy_repr import RepresentableBase
# from sqlalchemy_utils import database_exists, create_database, drop_database
# from marshmallow_sqlalchemy import ModelSchema
# # docker run --name cel-postgres -p 5432:5432 -e POSTGRES_USER=news -e POSTGRES_PASSWORD=pass -d postgres

# Base = declarative_base(cls=RepresentableBase)
# url = 'postgresql+psycopg2://news:pass@localhost/news'
# engine = create_engine(url, echo=True, pool_size=10, max_overflow=20)
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
