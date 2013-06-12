#!./env/bin/python

from recipebook import app, config

if __name__ == '__main__':
    app = app.create_app(config, testing=False)
    app.run(debug=config.DEBUG)
