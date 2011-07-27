from cookbook import db
from werkzeug import generate_password_hash
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


class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient = db.relationship("Ingredient", backref='recipe_association')
    amount = db.Column(db.Float)
    measure = db.Column(db.String(40))
    group = db.Column(db.ForeignKey('ingredient_groups.id'))

    def __init__(self,ingredient_name,amount,measure='',group=None):
        self.ingredient = _new_or_existing_ingredient(ingredient_name)
        self.amount = amount
        self.measure = measure
        self.group = group

#recipe_ingredients = db.Table('recipe_ingredients',
#        db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id')),
#        db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
#        db.Column('amount', db.Float),
#        db.Column('measure', db.String(40)),
#        db.Column('group', db.ForeignKey('ingredient_groups.id')),
#)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    titleslug = db.Column(db.String)
    description = db.Column(db.Text)
    photo = db.Column(db.String)
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #ingredients = db.relationship('Ingredient',
    #        secondary=recipe_ingredients, backref=db.backref('ingredient_recipes'))
    ingredients = db.relationship(RecipeIngredient, backref='recipes')

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


class CaseInsensitiveWord(Comparator):
    "Hybrid value representing a lower case representation of a word."

    def __init__(self, word):
        if isinstance(word, basestring):
            self.word = word.lower()
        elif isinstance(word, CaseInsensitiveWord):
            self.word = word.word
        else:
            self.word = db.func.lower(word)

    def operate(self, op, other):
        if not isinstance(other, CaseInsensitiveWord):
            other = CaseInsensitiveWord(other)
        return op(self.word, other.word)

    def __clause_element__(self):
        return self.word

    def __str__(self):
        return self.word

    key = 'name'
    "Label to apply to Query tuple results"


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    #Allow comparing case insensitive
    @hybrid_property
    def name_insensitive(self):
        return CaseInsensitiveWord(self.name)


class IngredientGroup(db.Model):
    __tablename__ = 'ingredient_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


def _new_or_existing_ingredient(name):
    """Return an existing ingredient that matches or create a new one"""
    try:
        ingredient = Ingredient.query.filter_by(name_insensitive=name).one()
    except NoResultFound:
        ingredient = Ingredient(name)
        db.session.add(ingredient)
        #don't commit now, that should be done elsewhere
    return ingredient


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def _slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
