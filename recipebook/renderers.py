"""
Module used for rendering models before passing to templates
"""

from flask import escape
import markdown2

from recipebook.models import Recipe
from recipebook import photos


class RecipeView(object):
    """
    An html view of a recipe
    """

    def __init__(self, recipe):
        self.recipe = recipe
        # Copy attributes required for views
        self.title = recipe.title
        self.title_slug = recipe.title_slug
        self.user = recipe.user
        self.photo = recipe.photo
        self.description = recipe.description
        self.tags = recipe.tags

        self.ingredient_groups = [
                IngredientGroupView(group)
                for group in recipe.ingredient_groups]

        self.general_ingredients = [
                render_ingredient(ingredient) for
                ingredient in recipe.general_ingredients]

    def show_photo(self, width, height):
        return photos.url(self.recipe.photo, width, height)

    def html_instructions(self):
        return markdown2.markdown(escape(self.recipe.instructions))


class IngredientGroupView(object):
    """
    An html view of an ingredient group
    """

    def __init__(self, recipe_ingredient_group):
        self.title = recipe_ingredient_group.title
        self.ingredients = [
                render_ingredient(ingredient) for
                ingredient in recipe_ingredient_group.ingredients]


def render_ingredient(ingredient):
    """
    HTML rendering of ingredient
    """

    if ingredient.amount:
        amount = render_amount(ingredient.amount)
    else:
        amount = None

    if ingredient.measure:
        measure = escape(ingredient.measure)
    else:
        measure = None

    item = escape(ingredient.item)
    return " ".join(
            s for s in (amount, measure, item) if s)


def render_amount(value):
    """
    Render a floating point value neatly in html
    using a fraction if possible.
    """

    tol = 1.0e-4
    whole_number = int(value)
    remainder = value - float(whole_number)

    # A whole number, return integer representation
    if abs(remainder) < tol:
        return "%d" % int(value)

    if whole_number == 0:
        initial = ""
    else:
        initial = "%d " % whole_number

    # Could use html entities, eg. &frac12; for 1/2, 1/4 and
    # 3/4 but they look different to fractions using &frasl;
    # so we'll keep it all consistent. Need to make sure the
    # line height is high enough so that the fractions don't
    # make the lines taller and uneven.
    frac_html = None
    fraction = find_fraction(remainder, tol)
    if fraction:
        frac_html = "<sup>%d</sup>&frasl;<sub>%d</sub>" % fraction
        return "%s%s" % (initial, frac_html)
    else:
        # Just return the floating point representation
        return "%.3f" % value


def find_fraction(value, tol):
    denominators = [2, 3, 4, 5, 6, 8]
    for denominator in denominators:
        for numerator in xrange(1, denominator):
            frac_value = float(numerator) / float(denominator)
            if abs(frac_value - value) < tol:
                return numerator, denominator
    return None
