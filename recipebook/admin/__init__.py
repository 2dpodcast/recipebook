from flask import Blueprint, session, abort

from recipebook import models

admin = Blueprint('admin', __name__)

@admin.before_request
def restrict_to_admin():
    pass
    if 'user_id' not in session:
        abort(401)
    user = models.User.query.filter_by(id=session['user_id']).one()
    if user.level != models.User.ADMIN:
        abort(401)

import recipebook.admin.views
