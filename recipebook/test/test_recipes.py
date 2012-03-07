import os
import unittest

from mongokit import Connection

from recipebook import models, config
from recipebook import app as recipeapp


class RecipebookTestCase(unittest.TestCase):
    def setUp(self):
        # Disable CSRF to be able to test posting to forms
        config.CSRF_ENABLED = False
        app = recipeapp.create_app(config, testing=True)
        app.test_request_context().push()
        connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
        connection.drop_database(config.TEST_DATABASE)
        self.app = app.test_client()

    def tearDown(self):
        connection.drop_database(config.TEST_DATABASE)

    def add_users(self):
        # Add some test uers
        admin_user = models.User(
                'admin@nonexistent.com', 'admin', 'admin', models.User.ADMIN)
        test_user = models.User(
                'tester@nonexistent.com', 'tester', 'tester', models.User.USER)
        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.commit()

    def test_invalid_user(self):
        test_email = 'test_invalid@test.com'
        rv = self.app.post('/register', data={
                'email': test_email,
                'username': config.DISABLED_USERNAMES[1],
                'realname': 'Tester',
                'password': '12345'},
            follow_redirects=True)
        assert 'not allowed' in rv.data
        assert models.User.query.filter_by(email=test_email).first() == None

    def test_add_users(self):
        self.add_users()

    def test_add_recipe(self):
        ingredients = [
            models.Ingredient('Mince', 500.0, 'g'),
            models.Ingredient('Spaghetti', 200.0, 'g'),
        ]
        for ingredient in ingredients:
            db.session.add(ingredient)
        recipe = models.Recipe(
                'Test Recipe', 1, ingredients, 'A new test recipe')
        db.session.add(recipe)
        db.session.commit()
        assert(models.Recipe.query.get(1).title == 'Test Recipe')
        assert(models.Recipe.query.get(1).ingredients[0].name == 'Mince')


if __name__ == '__main__':
    unittest.main()