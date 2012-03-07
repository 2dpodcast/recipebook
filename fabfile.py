execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

from mongokit import Connection
from recipebook import app, models, config
from fabric.api import *

def populate():
    """Populate database with test data"""

    app = app.create_app(config)
    app.test_request_context().push()

    connection = Connection(config.MONGODB_HOST, config.MONGODB_PORT)
    connection.register([models.User, models.Recipe])
    connection.drop_database[config.DATABASE]
    db = connection[app.database]

    admin = models.User(
            'admin@nonexistent.com', 'admin', 'admin', models.User.ADMIN)
    db.session.add(admin)
    ingredients = [
        models.Ingredient('Mince', 500.0, 'g'),
        models.Ingredient('Spaghetti', 200.0, 'g'),
    ]
    for ingredient in ingredients:
        db.session.add(ingredient)
    recipe1 = models.Recipe('Test Recipe', 1, ingredients, 'A new test recipe')
    recipe1.instructions = """- Boil spaghetti with salt for 10 mins.
- Brown the mince.
- Serve the mince on the spaghetti.
    """
    db.session.add(recipe1)
    db.session.commit()
    ingredients = [
        models.Ingredient('MINCE', 1.0, 'kg'),
        models.Ingredient('Toasted Bread', 2, 'slices'),
    ]
    for ingredient in ingredients:
        db.session.add(ingredient)
    recipe2 = models.Recipe(
            'Second Recipe', 1, ingredients, 'A second test recipe')
    db.session.add(recipe2)
    db.session.commit()


def test():
    """Run tests"""

    local('./env/bin/python recipebook/test.py')
