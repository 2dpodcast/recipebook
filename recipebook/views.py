from flask import (
        render_template, url_for,
        abort, flash, redirect,
        request, current_app, g, session,
        Blueprint)
from mongoengine import connect

from recipebook import models, forms, config


recipes = Blueprint('recipes', __name__)
errors = Blueprint('errors', __name__)


@recipes.before_app_request
def before_request():
    """Check if user is logged in and connect to the database"""

    connect(current_app.config.DATABASE,
            host=current_app.config.MONGODB_HOST,
            port=current_app.config.MONGODB_PORT)
    g.user = None
    g.owner = False
    g.admin = False
    if 'user_id' in session:
        g.user = models.User.query.get(session['user_id'])
        if g.user.level == models.User.ADMIN:
            g.admin = True


@recipes.route('/')
def index():
    latest_recipes = (models.Recipe.query.order_by(
        db.desc(models.Recipe.date)).limit(config.NUMBER_HOME_RECIPES))
    return render_template('index.html', recipes=latest_recipes)


@recipes.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.Login(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        flash(u'Successfully logged in as %s' % form.user.username)
        session['user_id'] = form.user.id
        return redirect(url_for('recipes.index'))
    return render_template('login.html', form=form)


@recipes.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.Register(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        user = models.User(
                form.email.data, form.username.data,
                form.password.data, models.User.USER)
        user.realname = form.realname.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('recipes.login'))
    return render_template('register.html', form=form)


@recipes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('recipes.index'))


@recipes.route('/<username>')
def user_recipes(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    if g.user is not None and g.user.id == user.id:
        g.owner = True
    return render_template(
            'user_recipes.html', user=user, recipes=user.recipes.all())


@recipes.route('/<username>/<recipe_slug>')
def recipe(username, recipe_slug):
    user = models.User.query.filter_by(username=username).first_or_404()
    if g.user is not None and g.user.id == user.id:
        g.owner = True
    user_recipe = (models.Recipe.query.filter(db.and_(
        models.Recipe.user_id == user.id,
        models.Recipe.titleslug == recipe_slug)).first_or_404())
    return render_template('recipe.html', user=user, recipe=user_recipe)


@recipes.route('/<username>/<recipe_slug>/edit', methods=('GET', 'POST'))
def edit_recipe(username, recipe_slug):
    user = models.User.query.filter_by(username=username).first_or_404()
    if g.user is not None and g.user.id == user.id:
        g.owner = True
    elif g.admin:
        pass
    else:
        abort(401)
    user_recipe = models.Recipe.query.filter(db.and_(
            models.Recipe.user_id == user.id,
            models.Recipe.titleslug == recipe_slug)).first_or_404()
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
