#!/usr/bin/env python

from recipebook import app, config

if __name__ == '__main__':
    app = app.create_app(config, testing=True)
    app.run(debug=config.DEBUG)
