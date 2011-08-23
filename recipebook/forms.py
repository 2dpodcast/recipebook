from flaskext.wtf import Form, TextField, PasswordField, validators
from recipebook.models import User
from recipebook import db, config

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
    email = TextField('Email', validators = [validators.Email(message="Invalid email address provided")])
    username = TextField('User name', validators = [validators.Required(message="No user name provided"), validators.regexp(r'^[^@]*$',message="Invalid user name")])
    realname = TextField('Real name (optional)')
    password = PasswordField('Password', validators = [validators.Required(message="No password provided")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.username.data in config.DISABLED_USERNAMES:
            self.username.errors.append('Sorry, that user name is not allowed')
            return False

        user = User.query.filter(User.username==self.username.data).first()
        if user is not None:
            self.username.errors.append('That user name is already taken')
            return False

        user = User.query.filter(User.email==self.email.data).first()
        if user is not None:
            self.username.errors.append('A user with that email address is already registered')
            return False

        return True
