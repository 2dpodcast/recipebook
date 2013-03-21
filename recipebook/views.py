from flask import (
        render_template, url_for,
        abort, flash, redirect,
        request, current_app, g, session,
        Blueprint)
from mongoengine import connect
from mongoengine.queryset import DoesNotExist

from recipebook import models, forms, config


recipes = Blueprint('recipes', __name__)
errors = Blueprint('errors', __name__)


@recipes.before_app_request
def before_request():
    """Check if user is logged in and connect to the database"""

    connect(current_app.config['DATABASE'],
            host=current_app.config['MONGODB_HOST'],
            port=current_app.config['MONGODB_PORT'])
    g.user = None
    g.owner = False
    g.admin = False
    if 'user_id' in session:
        g.user = models.User.objects.with_id(session['user_id'])
        if g.user.level == models.User.ADMIN:
            g.admin = True


@recipes.route('/')
def index():
    latest_recipes = models.Recipe.objects.order_by('-date').limit(config.NUMBER_HOME_RECIPES)
    return render_template('index.html', recipes=latest_recipes)


@recipes.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.Login(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        flash(u'Successfully logged in as %s' % form.user.username)
        session['user_id'] = form.user.username
        return redirect(url_for('recipes.index'))
    return render_template('login.html', form=form)


@recipes.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.Register(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        user = models.User(
                email=form.email.data,
                username=form.username.data,
                real_name=form.realname.data,
                level=models.User.USER)
        user.set_password(form.password.data)
        db.save()
        return redirect(url_for('recipes.login'))
    return render_template('register.html', form=form)


@recipes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('recipes.index'))


@recipes.route('/<username>')
def user_recipes(username):
    try:
        user = models.User.objects.with_id(username)
    except DoesNotExist:
        abort(404)
    recipes = models.Recipe.objects(user=user)
    if g.user is not None and g.user.id == user.id:
        g.owner = True
    return render_template(
            'user_recipes.html', user=user, recipes=recipes)


@recipes.route('/<username>/<recipe_slug>')
def recipe(username, recipe_slug):
    try:
        user = models.User.objects.with_id(username)
    except DoesNotExist:
        abort(404)
    if g.user is not None and g.user.username == user.username:
        g.owner = True
    try:
        recipe = models.Recipe.objects(user=user, title_slug=recipe_slug).get()
    except DoesNotExist:
        abort(404)
    return render_template('recipe.html', user=user, recipe=recipe)


@recipes.route('/<username>/<recipe_slug>/edit', methods=('GET', 'POST'))
def edit_recipe(username, recipe_slug):
    try:
        user = models.User.objects.with_id(username)
    except DoesNotExist:
        abort(404)
    if g.user is not None and g.user.username == user.username:
        g.owner = True
    elif g.admin:
        pass
    else:
        abort(401)
    try:
        user_recipe = models.Recipe.objects(user=user, title_slug=recipe_slug).get()
    except DoesNotExist:
        abort(404)
    form = forms.RecipeEdit(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        user_recipe.photo = form.save_photo()
        db.session.commit()
        return redirect(url_for(
            'recipes.recipe', username=username, recipe_slug=recipe_slug))
    return render_template(
            'recipe_edit.html', user=user, recipe=user_recipe, form=form)


def not_found(error):
    return render_template('404.html'), 404


def access_denied(error):
    return render_template('401.html'), 401


error_handlers = [(404, not_found), (401, access_denied)]
