Django Freckle Budgets
============

A reusable Django app that allows to plan year budgets and track them via letsfreckle.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-freckle-budgets

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-freckle-budgets.git#egg=freckle_budgets

TODO: Describe further installation steps (edit / remove the examples below):

Add ``freckle_budgets`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'freckle_budgets',
    )

Add the ``freckle_budgets`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^freckle-budgets/', include('freckle_budgets.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load freckle_budgets_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate freckle_budgets


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-freckle-budgets
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
