"""The only sript yet.

It would be devided in the future.

Useful commands:
    celery -A run:celery worker -Q hipri --loglevel=info
    docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3
"""

import os
import tempfile
from time import sleep

from celery import Celery
import celeryconfig

import flask
from flask import Flask, request, abort, redirect, url_for, send_file
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO, emit, join_room, rooms
from werkzeug import secure_filename

from PIL import Image



app = Flask(__name__, static_folder='dist', static_url_path='')
app.config['SECRET_KEY'] = 'there is no secret'

socketio = SocketIO(app, message_queue='amqp://user:password@localhost//')

celery = Celery('newscenter')
celery.config_from_object(celeryconfig)


@celery.task(name='resize_image')
def resize_image(path_orig, path_resized, sizes, keep_aspect_ratio=True, remove_orig=False):
    """Optimize image size.

    Args:
        path_orig (str): path to original image file (can also be `io.BufferedRandom` type of stream)
        path_resized (str): path to optimized image to be created at
        sizes (tuple): a (width, height) of the optimized image
        keep_aspect_ratio (bool): if set, fit image into `sizes`, but preserve it's aspect ratio
    """
    sleep(2)
    try:
        img = Image.open(path_orig).convert('RGB')
        if keep_aspect_ratio:
            img.thumbnail(sizes, Image.ANTIALIAS)
        else:
            img = img.resize(sizes, Image.ANTIALIAS)
        img.save(path_resized, 'JPEG', optimize=True)  # WTF?! quality=80 makes it worse
        if remove_orig:
            os.remove(path_orig)
        socketio.emit('confirmation', {'connection_confirmation': 'life iz gud'}, namespace='/test')
    except Exception as e:
        socketio.emit('confirmation', {'connection_confirmation': str(e)}, namespace='/test')


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Resize image and copy to `uploads` folder.

    Each file is saved as temporary file, and then a celery task is called on it.
    This task resizes the temporary file and places it into `uploads` folder.
    """
    uploaded_files = flask.request.files.getlist('file[]')
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        fd, path = tempfile.mkstemp()
        Image.open(file.stream).save(path, 'JPEG', optimize=True)
        resize_image.delay(path, 'uploads/_' + filename, (300, 300), False)
    return ''


@socketio.on('connection', namespace='/test')
def confirmation_message(message):
    print(message)
    emit('confirmation', {'connection_confirmation': message['connection_confirmation']})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9998)
