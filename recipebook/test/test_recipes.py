import os
import unittest

from pymongo import Connection
from mongoengine import connect
from mongoengine.queryset import DoesNotExist

from recipebook import models, config
from recipebook import app as recipeapp
from recipebook.test.example_recipes import recipes as json_recipes


class RecipebookTestCase(unittest.TestCase):
    def setUp(self):
        # Disable CSRF to be able to test posting to forms
        config.CSRF_ENABLED = False
        app = recipeapp.create_app(config, testing=True)
        app.test_request_context().push()
        self.connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
        self.connection.drop_database(config.TEST_DATABASE)
        connect(config.TEST_DATABASE,
                host=config.MONGODB_HOST, port=config.MONGODB_PORT)
        self.app = app.test_client()

    def tearDown(self):
        self.connection.drop_database(config.TEST_DATABASE)

    def add_users(self):
        # Add some test uers
        admin_user = models.create_user(
                'admin@nonexistent.com', 'admin', 'admin', models.User.ADMIN)
        test_user = models.create_user(
                'tester@nonexistent.com', 'tester', 'tester', models.User.USER)
        admin_user.save()
        test_user.save()

    def load_recipes(self):
        for data in json_recipes:
            recipe = models.Recipe()
            recipe.load_json(data)
            recipe.save()

    def test_invalid_user(self):
        test_email = 'test_invalid@test.com'
        rv = self.app.post('/register', data={
                'email': test_email,
                'username': 'account',
                'realname': 'Tester',
                'password': '12345'},
            follow_redirects=True)
        assert 'not allowed' in rv.data
        self.assertRaises(
                DoesNotExist, models.User.objects(email=test_email).get)

    def test_add_users(self):
        self.add_users()
        admin_user = models.User.objects.with_id('admin')
        test_user = models.User.objects.with_id('tester')

    def test_load_json(self):
        self.add_users()
        self.load_recipes()

        recipe = models.Recipe.objects(title_slug='example-recipe').first()
        assert(recipe.ingredient_groups[0].ingredients[0].item ==
                'An ingredient')


if __name__ == '__main__':
    unittest.main()
