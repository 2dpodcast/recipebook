import os
import re

from flask.ext.wtf import Form
import wtforms as wtf

from recipebook.models import User, get_user
from recipebook import config, models, photos


def valid_username(form, field):
    if not re.match(r'[a-zA-Z0-9_\-]+', field.data):
        raise wtf.ValidationError("User name may contain only alphanumeric "
            "characters, hyphens and underscores")


def valid_photo(form, field):
    if not field.data:
        return
    if not photos.verify(field.data.stream):
        raise wtf.ValidationError("Photo is not a recognised image type")


class Login(Form):
    login = wtf.TextField(
            'Username or Email',
            validators=[wtf.validators.Required(
                message="No user name or email entered")])
    password = wtf.PasswordField(
            'Password',
            validators=[wtf.validators.Required(
                message="No password entered")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        # Regular validation
        rv = Form.validate(self)
        if not rv:
            return False

        user = get_user(self.login.data)
        if user is None:
            self.login.errors.append('Unknown user name or email address')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class Register(Form):
    email = wtf.TextField(
            'Email',
            validators=[wtf.validators.Email(
                message="Invalid email address provided")])
    username = wtf.TextField(
            'User name',
            validators=[wtf.validators.Required(
                message="No user name provided"), valid_username])
    realname = wtf.TextField('Real name (optional)')
    password = wtf.PasswordField(
            'Password',
            validators=[wtf.validators.Required(
                message="No password provided")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.username.data in config.DISABLED_USERNAMES:
            self.username.errors.append('Sorry, this user name is not allowed')
            return False

        user = User.objects(username=self.username.data).first()
        if user is not None:
            self.username.errors.append('This user name is already taken')
            return False

        user = User.objects(email=self.email.data).first()
        if user is not None:
            self.username.errors.append("A user with that email address "
                    "is already registered")
            return False

        return True


RECIPE_MIN_INGREDIENTS = 1
RECIPE_MAX_INGREDIENTS = 100
RECIPE_MIN_GROUPS = 0
RECIPE_MAX_GROUPS = 20


class IngredientForm(Form):
    amount = wtf.DecimalField("Amount", validators=[wtf.validators.Optional()])
    measure = wtf.TextField("Measure")
    item = wtf.TextField(
            "Ingredient", validators=[wtf.validators.Required(
                message="Ingredient name is required")])

    def __init__(self, *args, **kwargs):
        # These subforms don't need csrf verification as they're only
        # used within the RecipeEdit form, and we need to create new
        # ones programatically so don't want to have to add the csrf token.
        kwargs['csrf_enabled'] = False
        super(IngredientForm, self).__init__(*args, **kwargs)

    @staticmethod
    def from_model(ingredient):
        """
        Convert ingredient model to dictionary of values used
        for filling out form data
        """

        # Only include values that are actually set, otherwise
        # wtforms will not be happy with None values
        return {
                k: v
                for k, v in [
                    ('amount', ingredient.amount),
                    ('measure', ingredient.measure),
                    ('item', ingredient.item)]
                if v
                }

    @staticmethod
    def to_model(ingredient_form):
        """
        Convert an ingredient from the form data to an ingredient model
        """

        # This isn't a method as we don't have access to the actual
        # object but to the form data as a dictionary

        ingredient = models.Ingredient()
        # Set attributes to none rather than empty strings if not present
        if not ingredient_form['amount']:
            ingredient.amount = None
        else:
            ingredient.amount = float(ingredient_form['amount'])

        if not ingredient_form['measure']:
            ingredient.measure = None
        else:
            ingredient.measure = ingredient_form['measure']

        ingredient.item = ingredient_form['item']
        return ingredient


class IngredientGroup(Form):
    title = wtf.TextField("Group title", validators=[wtf.validators.Required(
            message="Ingredient group title is required")])
    ingredients = wtf.FieldList(
            wtf.FormField(IngredientForm),
            min_entries=RECIPE_MIN_INGREDIENTS,
            max_entries=RECIPE_MAX_INGREDIENTS)

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(IngredientGroup, self).__init__(*args, **kwargs)

    @staticmethod
    def from_model(ingredient_group):
        """
        Convert ingredient group model to dictionary of
        values used for filling out form data
        """

        return {
                'title': ingredient_group.title,
                'ingredients': [
                    Ingredient.from_model(i)
                    for i in ingredient_group.ingredients],
                }

    @staticmethod
    def to_model(ingredient_group_form):
        """
        Convert an ingredient group from the form data
        to an ingredient group model
        """

        ingredient_group = models.IngredientGroup()
        ingredient_group.title = ingredient_group_form['title']
        ingredient_group.ingredients = [
                Ingredient.to_model(i)
                for i in ingredient_group_form['ingredients']]
        return ingredient_group


class RecipeEdit(Form):
    MIN_INGREDIENTS = RECIPE_MIN_INGREDIENTS
    MIN_GROUPS = RECIPE_MIN_GROUPS

    title = wtf.TextAreaField('Title')
    description = wtf.TextAreaField('Description')
    instructions = wtf.TextAreaField('Instructions')
    photo = wtf.FileField('Photo') #, validators=[valid_photo])
    general_ingredients = wtf.FieldList(
            wtf.FormField(IngredientForm),
            min_entries=RECIPE_MIN_INGREDIENTS,
            max_entries=RECIPE_MAX_INGREDIENTS)
    ingredient_groups = wtf.FieldList(
            wtf.FormField(IngredientGroup),
            min_entries=RECIPE_MIN_GROUPS,
            max_entries=RECIPE_MAX_GROUPS)

    @classmethod
    def from_recipe(cls, recipe, *args, **orig_kwargs):
        kwargs = dict(orig_kwargs)
        kwargs['title'] = recipe.title
        kwargs['description'] = recipe.description
        kwargs['instructions'] = recipe.instructions
        kwargs['general_ingredients'] = [
                IngredientForm.from_model(i)
                for i in recipe.general_ingredients]
        kwargs['ingredient_groups'] = [
                IngredientGroupForm.from_model(g)
                for g in recipe.ingredient_groups]
        return cls(*args, **kwargs)

    def save_recipe(self, recipe):
        """
        Update a recipe from the form data
        """

        if self.photo.data:
            recipe.photo = photos.save(self.photo.data.stream)

        recipe.title = self.title.data
        recipe.description = self.description.data
        recipe.instructions = self.instructions.data
        recipe.general_ingredients = [
            IngredientForm.to_model(i)
            for i in self.general_ingredients.data]
        recipe.ingredient_groups = [
            IngredientGroupForm.to_model(g)
            for g in self.ingredient_groups.data]

        recipe.save()
