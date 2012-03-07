from flask import Flask


def create_app(config, testing=False):
    app = Flask('recipebook')

    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['MONGODB_HOST'] = config.MONGODB_HOST
    app.config['MONGODB_PORT'] = config.MONGODB_PORT

    if testing:
        app.config['DATABASE'] = config.TEST_DATABASE
        app.config['TESTING'] = True
    else:
        app.config['DATABASE'] = config.DATABASE

    # Import all the views
    from recipebook import admin
    from recipebook import views
    app.register_blueprint(admin.admin, url_prefix='/administer')
    app.register_blueprint(views.recipes)
    app.register_blueprint(views.errors)

    for eh in views.error_handlers:
        app.register_error_handler(eh[0], eh[1])

    return app
