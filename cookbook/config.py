#Default configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/cookbook.sqlite'
SQLALCHEMY_ECHO = True

SECRET_KEY = '12345'
DEBUG = True

#Prevent url clashes with usernames
DISABLED_USERNAMES = ['login','register','static','account','new','search']

#Override settings with local_config.py
try:
    from local_config import *
except ImportError:
    pass
