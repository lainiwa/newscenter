import os
import tempfile

from flask import request
from werkzeug import secure_filename

from . import main
from ..tasks import resize_image


def fileToPath(insecure_filename):
    """Get upload path for filename.

    Args:
       insecure_filename (str): original non-escaped filename
    """
    filename = os.path.splitext(secure_filename(insecure_filename))[0]
    return f'uploads/_{filename}.jpg'

@main.route('/')
def index():
    # return 'kek'
    # return main.send_static_file('__init__.py')
    return main.send_static_file('index.html')


@main.route('/upload', methods=['POST'])
def upload():
    """Resize image and copy to `uploads` folder.

    Each file is saved as temporary file, and then a celery task is called on it.
    This task resizes the temporary file and places it into `uploads` folder.
    """
    uploaded_files = request.files.getlist('file[]')
    for file in uploaded_files:
        # Save stream as temporary file
        fd, path = tempfile.mkstemp()
        with open(path, "wb") as out:
                out.write(file.stream.read())
        # Run task converting image
        resize_image.delay(
            path_orig=path, path_resized=fileToPath(file.filename),
            sizes=(300, 300), name=file.filename,
            keep_aspect_ratio=True, remove_orig=False
        )
    return ''


# @jwt_required
@main.route('/delete_image', methods=['POST'])
def delete_image():
    """Delete uploaded image from uploads folder by name."""
    path = fileToPath(request.json.get('filename', ''))
    # If path doesn't exist, return 404 error;
    # else remove the file
    if os.path.isfile(path):
        os.remove(path)
    else:
        return '', 404

    return ''
