import os
import re
import datetime
from unicodedata import normalize
import Image

from werkzeug import generate_password_hash, check_password_hash
from mongokit import Document
import markdown2

from recipebook import config


class User(Document):
    __collection__ = 'users'

    structure = {
        '_id': unicode,
        'email': unicode,
        'realname': unicode,
        'password': unicode,
        'level': int,
        'registration_data': datetime.datetime,
    }
    indexes = [
        {
            'fields': '_id',
            'unique': True,
        },
    ]
    default_values = {
        'level': 0,
        'registration_date': datetime.datetime.utcnow,
    }
    use_dot_notation = True

    #User levels
    (ADMIN, USER) = range(2)

    def __init__(self, email, username, password, level):
        self['email'] = email
        self['_id'] = username
        self['password'] = generate_password_hash(password)
        if level in range(2):
            self.level = level
        else:
            abort(500)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def display_name(self):
        return self.realname if self.realname else self.username

    @property
    def username(self):
        return self['_id']


class Recipe(Document):
    __collection__ = 'recipes'

    structure = {
        'title': unicode,
        'titleslug': unicode,
        'description': unicode,
        'photo': unicode,
        'instructions': unicode,
        'user': unicode,
        'tags': [unicode],
        'ingredient_groups': [(unicode, [{
            'amount': float,
            'measure': unicode,
            'name': unicode}])],
        'data': datetime.datetime,
    }

    indexes = [
        {
            'fields': ['user', 'titleslug'],
            'unique': True,
        },
    ]

    use_dot_notation = True

    def __init__(self, title, user_id, ingredients=None, description='',
            instructions='', photo=''):
        self.title = title
        self.titleslug = _slugify(title)
        self.user = user
        if ingredients is None:
            self.ingredients = []
        else:
            self.ingredients = ingredients
        self.description = description
        self.instructions = instructions
        self.photo = photo
        self.date = datetime.utcnow()

    def html_instructions(self):
        return markdown2.markdown(self.instructions)

    def show_photo(self, width, height):
        """ Return the path to a photo with the specified dimensions.
        If it doesn't exist, it is created
        """
        #PHOTO_PATH is used in rendered web page whereas PHOTO_DIRECTORY is
        # the full directory on the server
        resized_name = self.photo + '_%dx%d.jpg' % (width, height)
        resized_path = config.PHOTO_DIRECTORY + os.sep + resized_name
        if not os.path.isfile(resized_path):
            photo = Image.open(
                    config.PHOTO_DIRECTORY + os.sep + self.photo + '.jpg')

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


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def _slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
