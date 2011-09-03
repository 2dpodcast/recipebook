from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import recipebook.models

def create_app(config):
    app = Flask('recipebook')

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['TEST_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    db.init_app(app)

    import recipebook.admin
    import recipebook.views
    app.register_blueprint(admin.admin, url_prefix='/administer')
    app.register_blueprint(views.recipes)
    app.register_blueprint(views.errors)

    for eh in recipebook.views.error_handlers:
        app.register_error_handler(eh[0],eh[1])

    return app

