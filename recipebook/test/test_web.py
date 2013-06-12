import flask
import os
from collections import namedtuple
import unittest

from pymongo import Connection
from mongoengine import connect
from mongoengine.queryset import DoesNotExist

from recipebook import models, config
from recipebook import app as recipeapp
from recipebook.test.example_recipes import recipes as json_recipes


User = namedtuple('User', ('username', 'email', 'password', 'level'))
test_users = {
        'admin': User(
            'admin', 'admin@nonexistent.com', 'admin', models.User.ADMIN),
        'tester': User(
            'tester', 'tester@nonexistent.com', 'tester', models.User.USER),
        }

recipe_post_data = {
        'title': "New Title",
        'instructions': "New instructions",
        'general_ingredients-0-amount': 2.0,
        'general_ingredients-0-measure': "cups",
        'general_ingredients-0-item': "flour",
        }


class RecipebookTestCase(unittest.TestCase):
    def setUp(self):
        # Disable CSRF to be able to test posting to forms
        config.CSRF_ENABLED = False
        self.app = recipeapp.create_app(config, testing=True)
        self.connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
        self.connection.drop_database(config.TEST_DATABASE)
        connect(config.TEST_DATABASE,
                host=config.MONGODB_HOST, port=config.MONGODB_PORT)
        self.client = self.app.test_client()

        self.add_users()
        self.load_recipes()

    def tearDown(self):
        self.connection.drop_database(config.TEST_DATABASE)

    def add_users(self):
        # Add some test uers
        for (username, email, password, level) in test_users.itervalues():
            user = models.create_user(email, username, password, level)
            user.save()

    def load_recipes(self):
        for data in json_recipes:
            recipe = models.Recipe()
            recipe.load_json(data)
            recipe.save()

    def login(self, user):
        return self.client.post('/login', data={
                'login': test_users[user].username,
                'password': test_users[user].password,
            }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_invalid_user(self):
        test_email = 'test_invalid@test.com'
        rv = self.client.post('/register', data={
                'email': test_email,
                'username': 'account',
                'realname': 'Tester',
                'password': '12345'},
            follow_redirects=True)
        assert 'not allowed' in rv.data
        self.assertRaises(
                DoesNotExist, models.User.objects(email=test_email).get)

    def test_add_users(self):
        admin_user = models.User.objects.with_id('admin')
        test_user = models.User.objects.with_id('tester')

    def test_login_logout(self):
        rv = self.login('admin')
        assert rv.status_code == 200
        with self.client:
            self.client.get('/')
            assert flask.g.user.username == 'admin'
            assert flask.g.admin
        rv = self.logout()
        assert rv.status_code == 200
        with self.client:
            self.client.get('/')
            assert flask.g.user is None
            assert not flask.g.admin
        rv = self.login('tester')
        assert rv.status_code == 200
        rv = self.logout()
        assert rv.status_code == 200

    def test_load_json(self):
        """
        Test loading a recipe from JSON data
        """

        # Recipes are always loaded in setup
        recipe = models.Recipe.objects(title_slug='example-recipe').first()
        assert(recipe.ingredient_groups[0].ingredients[0].item ==
                'An ingredient')

    def test_access_edit_form(self):
        """
        Test user access to editing a recipe
        """

        # Not logged in, not allowed
        rv = self.client.get('/admin/example-recipe/edit')
        assert rv.status_code == 401

        # Logged in as author, allowed
        rv = self.login('admin')
        rv = self.client.get('/admin/example-recipe/edit')
        assert rv.status_code == 200
        rv = self.logout()

        # Logged in as different user, not allowed
        rv = self.login('tester')
        rv = self.client.get('/admin/example-recipe/edit')
        assert rv.status_code == 401
        rv = self.logout()

    def test_setup_edit_form(self):
        """
        Check recipe data is entered into editing form
        """

        rv = self.login('admin')
        rv = self.client.get('/admin/example-recipe/edit')
        title_input = ('<textarea id="title" name="title">'
                'Example Recipe</textarea>')
        ingredient_input = 'value="An ingredient"'
        ingredient_input_2 = 'value="cups"'
        assert title_input in rv.data
        assert ingredient_input in rv.data
        assert ingredient_input_2 in rv.data

    def test_recipe_edit(self):
        """Test editing a recipe"""

        rv = self.login('admin')
        rv = self.client.post('/admin/example-recipe/edit',
                data=recipe_post_data)
        recipe = models.Recipe.objects(title="New Title").first()
        assert recipe
        assert recipe.instructions == "New instructions"
        assert recipe.general_ingredients[0].item == "flour"

    def test_new_recipe_access(self):
        """
        Test new recipe creation
        """

        rv = self.client.get('/new')
        assert rv.status_code == 401

        # Also make sure posting data isn't allowed
        rv = self.client.post('/new', data={})
        assert rv.status_code == 401

        rv = self.login('tester')
        rv = self.client.get('/new')
        assert rv.status_code == 200
        rv = self.logout()

    def test_new_recipe(self):
        """
        Test creating a new recipe
        """

        rv = self.login('tester')
        rv = self.client.post('/new',
                data=recipe_post_data)
        recipe = models.Recipe.objects(title="New Title").first()
        assert recipe
        assert recipe.instructions == "New instructions"
        assert recipe.general_ingredients[0].item == "flour"
        assert recipe.user.username == "tester"


if __name__ == '__main__':
    unittest.main()
