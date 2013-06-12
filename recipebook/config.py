# Default configuration

# Database
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DATABASE = 'recipebook'
TEST_DATABASE = 'recipebook'

SECRET_KEY = '12345'
DEBUG = True

# Forms
CSRF_ENABLED = True

# Prevent url clashes with usernames
DISABLED_USERNAMES = [
    'login', 'logout', 'register', 'account', 'new', 'search',
    'static', 'p', 'administer']

NUMBER_HOME_RECIPES = 10

# Max content size in bytes
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
PHOTO_DIRECTORY = 'recipebook/static/photos'
PHOTO_PATH = '/static/photos'

# Override settings with local_config.py
try:
    from local_config import *
except ImportError:
    pass
