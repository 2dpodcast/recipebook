RecipeBook
==========

A web application for sharing recipes.

Just mucking around with the Flask web framework,
this isn't usable.


Getting Started with Development
--------------------------------

To set up a virtualenv for development::

    virtualenv --no-site-packages env
    source env/bin/activate
    pip install -E env -r requirements.txt

Then initialise a database with some test data::

    fab devinit

To run tests everything::

    fab test

To run a development server for testing::

    ./runserver
