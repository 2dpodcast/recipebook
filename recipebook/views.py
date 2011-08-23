from recipebook import models, forms, db, config
from flask import render_template, request, abort, Blueprint, g, session, redirect, url_for, flash

recipes = Blueprint('recipes',__name__)
errors = Blueprint('errors',__name__)

@recipes.before_app_request
def before_request():
    """Check if user is logged in"""
    g.user = None
    if 'user_id' in session:
        g.user = models.User.query.filter_by(id=session['user_id']).one()


@recipes.route('/')
def index():
    return render_template('index.html')


@recipes.route('/login', methods=('GET','POST'))
def login():
    form = forms.Login(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        flash(u'Successfully logged in as %s' % form.user.username)
        session['user_id'] = form.user.id
        return redirect(url_for('recipes.index'))
    return render_template('login.html', form=form)


@recipes.route('/register', methods=('GET','POST'))
def register():
    form = forms.Register(request.form, csrf_enabled=config.CSRF_ENABLED)
    if request.method == 'POST' and form.validate():
        user = models.User(form.email.data, form.username.data, form.password.data, models.User.USER)
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
    return render_template('user_recipes.html')


@recipes.route('/<username>/<recipe>')
def recipe(username,recipe):
    return render_template('recipe.html')


def not_found(error):
    return render_template('404.html'), 404


def access_denied(error):
    return render_template('401.html'), 401


error_handlers = [(404,not_found),(401,access_denied)]

