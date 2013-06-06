# Use virtualenv:
execfile('./env/bin/activate_this.py',
    dict(__file__='./env/bin/activate_this.py'))

from argparse import ArgumentParser
from pymongo import Connection
from mongoengine import connect, ValidationError

from recipebook.importexport import load_gourmet
from recipebook import app as recipeapp
from recipebook import config, models


def import_gourmet(file_path, username):
    user = models.User.objects.with_id(username)
    with open(file_path) as gxml:
        for recipe in load_gourmet(gxml):
            recipe.user = user
            recipe.save()


def setup_connection():
    """Connect to mongodb"""
    connect(config.DATABASE,
            host=config.MONGODB_HOST, port=config.MONGODB_PORT)


if __name__ == '__main__':
    arg_parser = ArgumentParser(
            description="Import recipes from Gourmet XML files")
    arg_parser.add_argument('user',
            help="The user account to add the recipes to")
    arg_parser.add_argument('file',
            help="The Gourmet XML file to import")
    args = arg_parser.parse_args()

    setup_connection()
    import_gourmet(args.file, args.user)
