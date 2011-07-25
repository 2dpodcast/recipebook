from cookbook import app, db
from werkzeug import generate_password_hash


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


recipe_ingredients = db.Table('recipe_ingredients',
        db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id')),
        db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'))
)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    photo = db.Column(db.String)
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ingredients = db.relationship('Ingredient',
            secondary=recipe_ingredients, backref=db.backref('ingredient_recipes'))


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    measure = db.Column(db.String(50))


