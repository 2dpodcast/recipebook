execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

from mongokit import Connection
from recipebook import models, config
from recipebook import app as recipeapp
from recipebook.test import example_recipes
from fabric.api import *


def populate():
    """Populate database with test data"""

    app = recipeapp.create_app(config)
    app.test_request_context().push()

    connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
    connection.register([models.User, models.Recipe])
    connection.drop_database(config.DATABASE)
    db = connection[config.DATABASE]

    admin = db.User()
    admin.email = u'admin@nonexistent.com'
    admin.username = u'admin'
    admin.set_password(u'admin')
    admin.level = models.User.ADMIN
    admin.save()

    for recipe_data in example_recipes.recipes:
        recipe = db.Recipe()
        recipe.load_json(recipe_data)
        recipe.save()


def test():
    """Run tests"""

    local('./env/bin/python recipebook/test/test_recipes.py')
