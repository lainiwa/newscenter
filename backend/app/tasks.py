import os
from PIL import Image
from time import sleep

from . import celery, socketio


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
