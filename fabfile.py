execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

import datetime
from pymongo import Connection
from mongoengine import connect, ValidationError
from recipebook import models, config
from recipebook import app as recipeapp
from recipebook.test import example_recipes
from fabric.api import *


def build():
    # Build static files
    less_files = ['screen.less']
    input_dir = './recipebook/style/'
    output_dir = './recipebook/static/'
    for less_file in less_files:
        output = output_dir + less_file.replace('.less', '.css')
        local('lessc %s > %s' % (input_dir + less_file, output))


def _connect():
    # Connect with mongoengine
    connect(config.DATABASE,
            host=config.MONGODB_HOST, port=config.MONGODB_PORT)


def empty():
    """Delete database"""

    # Clear database if it exists, can't do this through mongoengine
    connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
    connection.drop_database(config.DATABASE)


def add_admin():
    _connect()
    admin = models.User(
            username='admin',
            email='admin@nonexistent.com',
            level=models.User.ADMIN)
    admin.set_password('admin')
    admin.save()


def populate():
    """Populate database with test data"""
    _connect()
    _add_admin()

    for recipe_data in example_recipes.recipes:
        recipe = models.Recipe()
        recipe.load_json(recipe_data)
        recipe.date_added = datetime.datetime.utcnow()
        recipe.save()


def test():
    """Run tests"""

    local('./env/bin/python recipebook/test/test_recipes.py')
