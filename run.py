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

import IPython



app = Flask(__name__, static_folder='dist', static_url_path='')
app.config['SECRET_KEY'] = 'there is no secret'

socketio = SocketIO(app, message_queue='amqp://user:password@localhost//')

celery = Celery('newscenter')
celery.config_from_object(celeryconfig)


@celery.task(name='resize_image')
def resize_image(path_orig, path_resized, sizes, name, keep_aspect_ratio=True, remove_orig=False):
    """Optimize image size.

    Args:
        path_orig (str): path to original image file (can also be `io.BufferedRandom` type of stream)
        path_resized (str): path to optimized image to be created at
        sizes (tuple): a (width, height) of the optimized image
        keep_aspect_ratio (bool): if set, fit image into `sizes`, but preserve it's aspect ratio
    """
    sleep(2)
    try:
        # Open image
        img = Image.open(path_orig).convert('RGB')
        # Apply ratio setting
        if keep_aspect_ratio:
            img.thumbnail(sizes, Image.ANTIALIAS)
        else:
            img = img.resize(sizes, Image.ANTIALIAS)
        # Save formatted as JPEG
        img.save(path_resized, 'JPEG', optimize=True)  # WTF?! quality=80 makes it worse
        # Emit message of successfull upload
        socketio.emit('confirmation', {'image': name, 'success': True}, namespace='/test')

    except Exception as e:
        # Emit message of error
        print('===exception===')
        socketio.emit('confirmation', {'image': name, 'success': False}, namespace='/test')

    finally:
        # Remove original file if appropriate flag is True
        print('===remove section===')
        if remove_orig:
            os.remove(path_orig)


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
        # Filename with chopped off extension
        filename = os.path.splitext(secure_filename(file.filename))[0]
        # Save stream as temporary file
        fd, path = tempfile.mkstemp()
        with open(path, "wb") as out:
                out.write(file.stream.read())
        # Run task converting image
        resize_image.delay(
            path_orig=path, path_resized=f'uploads/_{filename}.jpg',
            sizes=(300, 300), name=file.filename,
            keep_aspect_ratio=True, remove_orig=False
        )
    return ''


@app.route('/delete_image', methods=['POST'])
def delete_image():
    # insecure_filename = request.form['filename']
    insecure_filename = request.json.get('filename', '')
    filename = os.path.splitext(secure_filename(insecure_filename))[0]
    path = f'uploads/_{filename}.jpg'
    print(insecure_filename)
    print(path)
    if os.path.isfile(path):
        os.remove(path)
    else:
        return '', 404
    return ''


@socketio.on('connection', namespace='/test')
def confirmation_message(message):
    print(message)
    # emit('confirmation', {'connection_confirmation': message['connection_confirmation']})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9998)
