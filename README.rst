RecipeBook
==========

A web application for sharing recipes built with
Flask and MongoDB.

It is currently usable but still a work in progress.

Getting Started with Development
--------------------------------

To set up a Python virtualenv for development::

    virtualenv --no-site-packages env
    source env/bin/activate
    pip install -r requirements.txt

To install MongoDB on Fedora::

    sudo yum install mongodb mongodb-server
    sudo systemctl enable mongod.service
    sudo systemctl start mongod.service

Then initialise a database with some test data::

    fab populate

To run tests::

    fab test

To run a development server for testing::

    ./runserver
