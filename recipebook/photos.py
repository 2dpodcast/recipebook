"""
Utilities for working with photos
"""

from hashlib import sha1
import os
from PIL import Image

from recipebook import config

# We use Pillow rather than PIL.
# For some reason PIL fails to read data in an io.BytesIO file,
# and Pillow seems much better maintained.

# Maximum dimension when saving images
MAX_ALLOWED_DIM = 1024


def url(name, width, height):
    """ Return the path to a photo with the specified dimensions.
    If it doesn't exist, it is created
    """

    # PHOTO_PATH is used in rendered web page whereas PHOTO_DIRECTORY is
    # the full directory on the server
    resized_name = name + '_%dx%d.jpg' % (width, height)
    resized_path = config.PHOTO_DIRECTORY + os.sep + resized_name
    if not os.path.isfile(resized_path):
        photo = Image.open(
                config.PHOTO_DIRECTORY + os.sep + name + '.jpg')

        current_ratio = float(photo.size[0]) / float(photo.size[1])
        desired_ratio = float(width) / float(height)
        box = [0, 0, photo.size[0], photo.size[1]]

        if current_ratio > desired_ratio:
            width_crop = int(round(
                (photo.size[0] - desired_ratio * photo.size[1]) / 2.))
            box[0] = width_crop
            box[2] -= width_crop
        else:
            height_crop = int(round(
                (photo.size[1] - photo.size[0] / desired_ratio) / 2.))
            box[1] = height_crop
            box[3] -= height_crop

        resized_photo = photo.crop(box).resize(
                (width, height), Image.BILINEAR)

        resized_photo.save(resized_path)
    return config.PHOTO_PATH + os.sep + resized_name


def verify(data):
    """
    Check a file contains a valid image
    """

    try:
        image = Image.open(data)
        image.verify()
        # Image can't be used after calling verify, so we have to open
        # it again later, seek to the start now so we can re-use file
        data.seek(0)
        return True
    except:
        return False


def save(data):
    """
    Save a file type object to a photo on disk and return the name
    (minus the extension) for using later to retrieve with the url
    function.

    Data must have been previously verified.
    """

    image = Image.open(data)
    # Resize image if it is too large
    max_dim = max(image.size)
    if max_dim > MAX_ALLOWED_DIM:
        scale = MAX_ALLOWED_DIM / max_dim
        new_dims = [int(dim * scale) for dim in image.size]
        image = image.resize(new_dims, Image.BILINEAR)
    file_hash = sha1(image.tostring()).hexdigest()
    output_path = config.PHOTO_DIRECTORY + os.sep + file_hash + '.jpg'
    image.save(output_path)
    return file_hash
