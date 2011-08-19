from flaskext.wtf import Form, TextField, PasswordField, validators
from recipebook.models import User
from recipebook import db

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
            self.login.errors.append('Unknown username or email address')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True

class Register(Form):
    email = TextField('Email', validators = [validators.Email(message="Invalid email address provided")])
    username = TextField('User name', validators = [validators.Required(message="No user name provided"), validators.regexp(r'^[^@]*$',message="Invalid username")])
    realname = TextField('Real name (optional)')
    password = PasswordField('Password', validators = [validators.Required(message="No password provided")])
