import os
import unittest
import tempfile
from flaskext.sqlalchemy import SQLAlchemy
from cookbook import app, models

class CookbookTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_path
        app.config['SQLALCHEMY_ECHO'] = True
        app.config['TESTING'] = True

        self.app = app.test_client()

        self.db = SQLAlchemy(app)
        app.test_request_context().push()
        self.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def add_users(self):
        #Add some test uers
        admin_user = models.User('admin@nonexistent.com','admin','admin',models.User.ADMIN)
        test_user = models.User('tester@nonexistent.com','tester','tester',models.User.USER)
        self.db.session.add(admin_user)
        self.db.session.add(test_user)
        self.db.session.commit()

    def test_setup(self):
        pass

    def test_add_users(self):
        self.add_users()

    #def test_add_recipe(self):
    #    ingredients = [
    #        models.RecipeIngredient('Mince',500.0,'g'),
    #        models.RecipeIngredient('Spaghetti',200.0,'g'),
    #    ]
    #    recipe = models.Recipe('Test Recipe',1,ingredients,'A new test recipe')
    #    self.db.session.add(recipe)
    #    self.db.session.commit()
    #    assert(models.Recipe.query.get(1).name == 'Test Recipe')


if __name__ == '__main__':
    unittest.main()
