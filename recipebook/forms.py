from flaskext.wtf import Form, TextField, FileField, PasswordField, validators, ValidationError
from recipebook.models import User
from recipebook import db, config
import re
from hashlib import sha1
import Image
import os

def valid_username(form, field):
    if not re.match(r'[a-zA-Z0-9_\-]+', field.data):
        raise ValidationError("User name may contain only alphanumeric characters, hyphens and underscores")


def valid_photo(form, field):
    try:
        field.image = Image.open(field.file)
    except:
        raise ValidationError("Photo is not a recognised image type")


class Login(Form):
    login = TextField('Username or Email', validators = [validators.Required(message="No user name or email entered")])
    password = PasswordField('Password', validators = [validators.Required(message="No password entered")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        # regular validation
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter(db.or_(User.username==self.login.data, User.email==self.login.data)).first()
        if user is None:
            self.login.errors.append('Unknown user name or email address')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class Register(Form):
    email = TextField('Email',validators = [validators.Email(message="Invalid email address provided")])
    username = TextField('User name', validators = [validators.Required(message="No user name provided"), valid_username])
    realname = TextField('Real name (optional)')
    password = PasswordField('Password', validators = [validators.Required(message="No password provided")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.username.data in config.DISABLED_USERNAMES:
            self.username.errors.append('Sorry, this user name is not allowed')
            return False

        user = User.query.filter(User.username==self.username.data).first()
        if user is not None:
            self.username.errors.append('This user name is already taken')
            return False

        user = User.query.filter(User.email==self.email.data).first()
        if user is not None:
            self.username.errors.append('A user with that email address is already registered')
            return False

        return True


class RecipeEdit(Form):
    #http://packages.python.org/Flask-WTF/field.file.filename
    #http://flask.pocoo.org/docs/patterns/fileuploads/
    #http://stackoverflow.com/questions/266648/python-check-if-uploaded-file-is-jpg
    title = TextField('Title',validators = [validators.Required(message="You must set a title for the recipe")])
    photo = FileField('Photo',validators = [valid_photo])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        return True

    def save_photo(self):
        try:
            image = self.photo.image
        except AttributeError:
            image = Image.open(self.photo.file)
        file_hash = sha1(image.tostring()).hexdigest()
        image.save(os.path.join(config.PHOTO_DIRECTORY, file_hash+'.jpg'))
        return file_hash

