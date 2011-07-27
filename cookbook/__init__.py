from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import cookbook.models

def create_app(config):
    app = Flask('cookbook')

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['TEST_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO
    app.config['SECRET_KEY'] = config.SECRET_KEY

    db.init_app(app)

    import cookbook.admin
    import cookbook.views
    app.register_blueprint(admin.admin, url_prefix='/administer')
    app.register_blueprint(views.recipes)
    app.register_blueprint(views.errors)

    for eh in cookbook.views.error_handlers:
        app.register_error_handler(eh[0],eh[1])

    return app

