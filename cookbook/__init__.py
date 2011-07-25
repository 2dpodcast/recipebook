from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO
app.config['SECRET_KEY'] = config.SECRET_KEY

db = SQLAlchemy(app)

import admin
app.register_blueprint(admin.admin, url_prefix='/administer')

import cookbook.views
import cookbook.models
