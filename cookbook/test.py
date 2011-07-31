import os
import unittest

from cookbook import db, models, create_app, config

class CookbookTestCase(unittest.TestCase):

    def setUp(self):
        config.SQLALCHEMY_DATABASE_URI = config.TEST_DATABASE_URI
        config.SQLALCHEMY_ECHO = True
        app = create_app(config)
        app.config['TESTING'] = True
        app.test_request_context().push()
        db.drop_all()
        db.create_all()
        self.app = app.test_client()

    def tearDown(self):
        pass

    def add_users(self):
        #Add some test uers
        admin_user = models.User('admin@nonexistent.com','admin','admin',models.User.ADMIN)
        test_user = models.User('tester@nonexistent.com','tester','tester',models.User.USER)
        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.commit()

    def test_add_users(self):
        self.add_users()

    def test_add_recipe(self):
        ingredients = [
            models.Ingredient('Mince',500.0,'g'),
            models.Ingredient('Spaghetti',200.0,'g'),
        ]
        for ingredient in ingredients:
            db.session.add(ingredient)
        recipe = models.Recipe('Test Recipe',1,ingredients,'A new test recipe')
        db.session.add(recipe)
        db.session.commit()
        assert(models.Recipe.query.get(1).title == 'Test Recipe')


if __name__ == '__main__':
    unittest.main()
