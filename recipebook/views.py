from recipebook import models
from flask import render_template, request, abort, Blueprint
from werkzeug import check_password_hash

recipes = Blueprint('recipes',__name__)
errors = Blueprint('errors',__name__)

@recipes.route('/')
def index():
    return render_template('index.html')


@recipes.route('/login')
def login():
    if request.method == 'POST':
        return ''
    else:
        return render_template('login.html')


@recipes.route('/register')
def register():
    if request.method == 'POST':
        return ''
    else:
        return render_template('register.html')


@recipes.route('/<username>')
def user_recipes(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    return render_template('user_recipes.html')


@recipes.route('/<username>/<recipe>')
def recipe(username,recipe):
    return render_template('recipe.html')


def not_found(error):
    return render_template('404.html'), 404


def access_denied(error):
    return render_template('401.html'), 401


error_handlers = [(404,not_found),(401,access_denied)]

