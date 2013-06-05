import os
import re
import datetime
from unicodedata import normalize
import Image

import json
from werkzeug import generate_password_hash, check_password_hash
from bson import json_util
from mongoengine import (
        Document, EmbeddedDocument, Q,
        StringField, EmailField, IntField, FloatField,
        DateTimeField, ListField, EmbeddedDocumentField, ReferenceField)
import markdown2

from recipebook import config


class User(Document):
    """Represents a user in the database"""

    username = StringField(primary_key=True)
    email = EmailField(required=True)
    real_name = StringField(default='')
    password = StringField(required=True)
    level = IntField(required=True, default=0)
    registration_date = DateTimeField()

    meta = {'collection': 'users'}

    #User levels
    (ADMIN, USER) = range(2)

    def set_password(self, password):
        self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def display_name(self):
        return self.real_name if self.real_name else self.username


def create_user(email, username, password, level=User.USER):
    user = User(email=email, username=username)
    if level in (User.USER, User.ADMIN):
        user.level = level
    else:
        raise ValueError("Invalid user level")
    user.set_password(password)
    return user


def get_user(login_name):
    """Get a user with either the username or email"""

    return User.objects(
        Q(username=login_name) |
        Q(email=login_name)).first()


class Ingredient(EmbeddedDocument):
    name = StringField(required=True)
    amount = FloatField()
    measure = StringField()


class IngredientGroup(EmbeddedDocument):
    title = StringField(default='')
    ingredients = ListField(EmbeddedDocumentField(Ingredient))

    def load_json(self, data):
        """Update data with dictionary from json data"""

        self.title = data['group']
        self.ingredients = []
        for ingredient in data['ingredients']:
            self.ingredients.append(Ingredient(
                name=ingredient['name'],
                amount=ingredient['amount'],
                measure=ingredient['measure']))


class Recipe(Document):
    """Represents a recipe document in the database"""

    title = StringField(required=True)
    title_slug = StringField(required=True, unique_with='user')
    description = StringField(default='')
    photo = StringField(default='')
    instructions = StringField()
    user = ReferenceField(User, dbref=True, required=True)
    tags = ListField(StringField())
    ingredient_groups = ListField(EmbeddedDocumentField(IngredientGroup))
    date_added = DateTimeField()

    meta = {
            'collection': 'recipes',
            'indexes': [('user', 'title_slug')],
    }

    def load_json(self, json_data):
        """Update data from json string"""

        data = json.loads(json_data, object_hook=json_util.object_hook)
        for key in data:
            if key == 'title':
                self.title = data[key]
                self.title_slug = _slugify(data[key])
            elif key == 'user':
                self.user = User.objects.get(username=data[key])
            elif key == 'ingredient_groups':
                self.ingredient_groups = []
                for group in data[key]:
                    ingredient_group = IngredientGroup()
                    ingredient_group.load_json(group)
                    self.ingredient_groups.append(ingredient_group)
            else:
                self.__setattr__(key, data[key])

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

    def group_ingredients(self):
        """Return a list of ingredient groups and ungrouped ingredients"""

        ungrouped_ingredients = []
        groups = []
        for group in self.ingredient_groups:
            if group.title == '':
                ungrouped_ingredients.extend(group.ingredients)
            else:
                groups.append(group)
        return (groups, ungrouped_ingredients)


def create_recipe(title, username, ingredients, description):
    """Create a new recipe

    ingredients is a dict with ingredient group names as keys
    and lists of ingredients for values
    """

    recipe = Recipe(title=title, description=description)
    recipe.user = User.objects.with_id(username)
    recipe.title_slug = _slugify(title)
    ingredient_groups = [
            IngredientGroup(group=k, ingredients=v)
            for k, v in ingredients.items()]
    recipe.ingredient_groups = ingredient_groups
    recipe.date = datetime.datetime.utcnow()
    return recipe


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def _slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""

    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
