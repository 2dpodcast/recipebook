execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

from cookbook import db, models

def devinit():
    db.drop_all()
    db.create_all()
    admin = models.User('admin@nonexistent.com','admin','admin',models.User.ADMIN)
    db.session.add(admin)
    ingredients = [
        models.RecipeIngredient('Mince',500.0,'g'),
        models.RecipeIngredient('Spaghetti',200.0,'g'),
    ]
    recipe1 = models.Recipe('Test Recipe',1,ingredients,'A new test recipe')
    db.session.add(recipe1)
    db.session.commit()
    ingredients = [
        models.RecipeIngredient('MINCE',1.0,'kg'),
        models.RecipeIngredient('Toasted Bread',2,'slices'),
    ]
    recipe2 = models.Recipe('Second Recipe',1,ingredients,'A second test recipe')
    db.session.add(recipe2)
    db.session.commit()
