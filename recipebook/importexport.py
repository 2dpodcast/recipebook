import base64
import datetime
# We use defusedxml as input is from untrusted users
try:
    from defusedxml.cElementTree import parse
except ImportError:
    from defusedxml.ElementTree import parse
from io import BytesIO
import os

from recipebook import config, photos
from recipebook.models import Recipe, Ingredient, IngredientGroup, slugify


def load_gourmet(gourmet_file):
    """
    Import a Gourmet XML file

    This may contain multiple recipes so this function
    is a generator that may return multiple recipes.

    The recipe won't have a user set so that needs
    to be set before saving it to the database.
    """

    tree = parse(gourmet_file)
    doc = tree.getroot()
    if doc.tag != 'gourmetDoc':
        raise ValueError("Document is not a Gourmet file")
    for recipe_elem in doc:
        if recipe_elem.tag != 'recipe':
            continue

        title = recipe_elem.find('title').text.strip()
        instructions = recipe_elem.find('instructions').text.strip()
        description = ''

        ingredient_list = recipe_elem.find('ingredient-list')
        general_ingredients = [
                _read_gourmet_ingredient(e)
                for e in ingredient_list
                if e.tag == 'ingredient']
        ingredient_groups = [
                _read_gourmet_ingredient_group(e)
                for e in ingredient_list
                if e.tag == 'inggroup']
        image = recipe_elem.find('image')

        if image is not None:
            image_format = image.attrib['format']
            image_b64_data = image.text.strip()
            image_data = BytesIO(base64.b64decode(image_b64_data))
            if photos.verify(image_data):
                image_name = photos.save(image_data)
            else:
                image_name = ''
        else:
            image_name = ''

        recipe = Recipe(
                title=title,
                title_slug=slugify(title),
                description='',
                instructions=instructions,
                date_added=datetime.datetime.utcnow(),
                general_ingredients=general_ingredients,
                ingredient_groups=ingredient_groups,
                photo=image_name)
        yield recipe


def _read_gourmet_ingredient(elem):
    items = {n.tag: n.text.strip() for n in elem}
    item = items['item']
    measure = items.get('unit', None)
    amount = items.get('amount', None)
    if amount is not None:
        amount = float(amount)
    return Ingredient(item=item, amount=amount, measure=measure)


def _read_gourmet_ingredient_group(elem):
    title = ''
    ingredients = []
    for node in elem:
        if node.tag == 'groupname':
            title = node.text.strip()
        elif node.tag == 'ingredient':
            ingredients.append(_read_gourmet_ingredient(node))
    return IngredientGroup(title=title, ingredients=ingredients)
