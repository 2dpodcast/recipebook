#!/usr/bin/env python

from recipebook import create_app, config

if __name__ == '__main__':
    app = create_app(config)
    app.run(debug=config.DEBUG)
