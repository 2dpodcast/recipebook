from recipebook import db, config
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound
import re
from unicodedata import normalize
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from flask import url_for
from datetime import datetime
import markdown2
import Image
import os

class User(db.Model):
    __tablename__ = 'users'

    #User levels
    (ADMIN,USER) = range(2)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    realname = db.Column(db.String)
    password = db.Column(db.String)
    level = db.Column(db.Integer)
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic')

    def __init__(self, email, username, password, level):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        if level in range(2):
            self.level = level
        else:
            abort(500)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def display_name(self):
        return self.realname if self.realname else self.username


recipe_tags = db.Table('recipe_tags',
        db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
        db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    titleslug = db.Column(db.String)
    description = db.Column(db.Text)
    photo = db.Column(db.String(50))
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tags = db.relationship('Tag',
            secondary=recipe_tags, backref=db.backref('tag_recipes'))
    ingredients = db.relationship('Ingredient', backref='recipe')
    date = db.Column(db.DateTime)

    def __init__(self, title, user_id, ingredients=None, description='', instructions='', photo=''):
        self.title = title
        self.titleslug = _slugify(title)
        #todo: check that titleslug is unique within user
        self.user_id = user_id
        if ingredients is None:
            self.ingredients = []
        else:
            self.ingredients = ingredients
        self.description = description
        self.instructions = instructions
        self.photo = photo
        self.date = datetime.now()

    def group_ingredients(self):
        """Return a list of groups of ingredients. Each group is
        a tuple of title and ingredients.
        """
        return (["",self.ingredients])

    def html_instructions(self):
        return markdown2.markdown(self.instructions)

    def show_photo(self,width,height):
        """ Return the path to a photo with the specified dimensions.
        If it doesn't exist, it is created
        """
        #PHOTO_PATH is used in rendered web page whereas PHOTO_DIRECTORY is the full directory on the server
        resized_name = self.photo+'_%dx%d.jpg' % (width,height)
        resized_path = config.PHOTO_DIRECTORY+os.sep+resized_name
        if not os.path.isfile(resized_path):
            photo = Image.open(config.PHOTO_DIRECTORY+os.sep+self.photo+'.jpg')

            current_ratio = float(photo.size[0]) / float(photo.size[1])
            desired_ratio = float(width) / float(height)
            box = [0, 0, photo.size[0], photo.size[1]]

            if current_ratio > desired_ratio:
                width_crop = int(round((photo.size[0] - desired_ratio * photo.size[1])/2.))
                box[0] = width_crop
                box[2] -= width_crop
            else:
                height_crop = int(round((photo.size[1] - photo.size[0] / desired_ratio)/2.))
                box[1] = height_crop
                box[3] -= height_crop

            resized_photo = photo.crop(box).resize((width,height),Image.BILINEAR)

            resized_photo.save(resized_path)
        return config.PHOTO_PATH+os.sep+resized_name


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    measure = db.Column(db.String(40))
    group_name = db.Column(db.String(150))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))

    def __init__(self, name, amount, measure='', group_name=''):
        self.name = name
        self.amount = amount
        self.measure = measure
        self.group_name = group_name


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def _slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
