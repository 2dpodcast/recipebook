execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

import datetime
from pymongo import Connection
from mongoengine import connect, ValidationError
from recipebook import models, config
from recipebook import app as recipeapp
from recipebook.test import example_recipes
from fabric.api import *


def populate():
    """Populate database with test data"""

    app = recipeapp.create_app(config)
    app.test_request_context().push()

    # Clear database if it exists, can't do this through mongoengine
    connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
    connection.drop_database(config.DATABASE)

    # Connect with mongoengine
    connect(config.DATABASE,
            host=config.MONGODB_HOST, port=config.MONGODB_PORT)

    admin = models.User(
            username='admin',
            email='admin@nonexistent.com',
            level=models.User.ADMIN)
    admin.set_password('admin')
    admin.save()

    for recipe_data in example_recipes.recipes:
        recipe = models.Recipe()
        recipe.load_json(recipe_data)
        recipe.date_added = datetime.datetime.utcnow()
        recipe.save()


def test():
    """Run tests"""

    local('./env/bin/python recipebook/test/test_recipes.py')
