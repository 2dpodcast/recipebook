execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

from cookbook import db, models

def devinit():
    db.drop_all()
    db.create_all()
    admin = models.User('admin@nonexistent.com','admin','admin',models.User.ADMIN)
    db.session.add(admin)
    db.session.commit()

