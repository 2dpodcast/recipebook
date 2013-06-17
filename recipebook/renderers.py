"""
Module used for rendering models before passing to templates
"""

from flask import escape
import markdown2

from recipebook import photos


def markdown(text):
    return markdown2.markdown(escape(text))


def show_photo(photo_name, width, height):
    return photos.url(photo_name, width, height)


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
    return " ".join(s for s in (amount, measure, item) if s)


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
