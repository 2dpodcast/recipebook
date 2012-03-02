#Default configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/recipebook.sqlite'
TEST_DATABASE_URI = 'sqlite:////tmp/recipebook_testing.sqlite'
SQLALCHEMY_ECHO = True

SECRET_KEY = '12345'
DEBUG = True
CSRF_ENABLED = True

#Prevent url clashes with usernames
DISABLED_USERNAMES = [
    'login', 'register', 'static', 'account', 'new', 'search', 'p']

NUMBER_HOME_RECIPES = 10

#Max content size in bytes
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
PHOTO_DIRECTORY = 'recipebook/static/photos'
PHOTO_PATH = '/static/photos'

#Override settings with local_config.py
try:
    from local_config import *
except ImportError:
    pass
