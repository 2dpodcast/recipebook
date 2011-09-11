from flaskext import wtf
from recipebook.models import User
from recipebook import db, config
import re
from hashlib import sha1
import Image
import os

def valid_username(form, field):
    if not re.match(r'[a-zA-Z0-9_\-]+', field.data):
        raise wtf.ValidationError("User name may contain only alphanumeric characters, hyphens and underscores")


def valid_photo(form, field):
    if field.file.filename == '':
        return
    try:
        field.image = Image.open(field.file)
        field.image.verify() # can't be used after calling verify
    except:
        raise wtf.ValidationError("Photo is not a recognised image type")


class Login(wtf.Form):
    login = wtf.TextField('Username or Email', validators = [wtf.validators.Required(message="No user name or email entered")])
    password = wtf.PasswordField('Password', validators = [wtf.validators.Required(message="No password entered")])

    def __init__(self, *args, **kwargs):
        wtf.Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        # regular validation
        rv = wtf.Form.validate(self)
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


class Register(wtf.Form):
    email = wtf.TextField('Email',validators = [wtf.validators.Email(message="Invalid email address provided")])
    username = wtf.TextField('User name', validators = [wtf.validators.Required(message="No user name provided"), valid_username])
    realname = wtf.TextField('Real name (optional)')
    password = wtf.PasswordField('Password', validators = [wtf.validators.Required(message="No password provided")])

    def validate(self):
        rv = wtf.Form.validate(self)
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


class IngredientForm(wtf.Form):
    amount = wtf.DecimalField("Amount", validators = [wtf.validators.Required(message="Ingredient amounts must be specified")])
    measure = wtf.TextField("Measure")
    ingredient = wtf.TextField("Ingredient", validators = [wtf.validators.Required(message="Ingredient names must be specified")])


class IngredientGroup(wtf.Form):
    title = wtf.TextField("Group title")
    ingredients = wtf.FieldList(wtf.FormField(IngredientForm),min_entries=3,max_entries=200)


class RecipeEdit(wtf.Form):
    MIN_INGREDIENTS = 3;
    MIN_GROUPS = 2;
    description = wtf.TextAreaField('Description')
    photo = wtf.FileField('Photo',validators = [valid_photo])
    general_ingredients = wtf.FormField(IngredientGroup)
    ingredient_groups = wtf.FieldList(wtf.FormField(IngredientGroup),min_entries=MIN_GROUPS,max_entries=20)

    def validate(self):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        return True

    def save_photo(self):
        self.photo.file.seek(0)
        image = Image.open(self.photo.file)
        file_hash = sha1(image.tostring()).hexdigest()
        image.save(os.path.join(config.PHOTO_DIRECTORY, file_hash+'.jpg'))
        return file_hash

