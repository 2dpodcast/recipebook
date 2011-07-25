from cookbook import app, models
from flask import render_template, request, abort
from werkzeug import check_password_hash
from sqlalchemy.orm.exc import NoResultFound


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if request.method == 'POST':
        return ''
    else:
        return render_template('login.html')


@app.route('/register')
def register():
    if request.method == 'POST':
        return ''
    else:
        return render_template('register.html')


@app.route('/<username>')
def user_recipes(username):
    try:
        user = models.User.query.filter_by(username=username).one()
        return render_template('user_recipes.html')
    except NoResultFound:
        abort(404)


@app.route('/<username>/<recipe>')
def recipe(username,recipe):
    return render_template('recipe.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(401)
def denied(error):
    return render_template('401.html'), 401
