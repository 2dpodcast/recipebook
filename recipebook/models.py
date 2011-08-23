from recipebook import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound
import re
from unicodedata import normalize
from sqlalchemy.ext.hybrid import Comparator, hybrid_property

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
    recipes = db.relationship('Recipe', backref='users', lazy='dynamic')

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
    photo = db.Column(db.String)
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tags = db.relationship('Tag',
            secondary=recipe_tags, backref=db.backref('tag_recipes'))
    ingredients = db.relationship('Ingredient', backref='recipes')

    def __init__(self, title, user_id, ingredients=None, description='', instructions='', photo=''):
        self.title = title
        self.titleslug = _slugify(title)
        #todo: check that titleslug is unique
        self.user_id = user_id
        if ingredients is None:
            self.ingredients = []
        else:
            self.ingredients = ingredients
        self.description = description
        self.instructions = instructions
        self.photo = photo

    def group_ingredients(self):
        return ([], self.ingredients)

    def html_instructions(self):
        return self.instructions


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    measure = db.Column(db.String(40))
    group_id = db.Column(db.Integer, db.ForeignKey('ingredient_groups.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))

    def __init__(self, name, amount, measure='', group=None):
        self.name = name
        self.amount = amount
        self.measure = measure
        self.group = group


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class IngredientGroup(db.Model):
    __tablename__ = 'ingredient_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def _slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
