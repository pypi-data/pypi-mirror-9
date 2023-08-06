=======================
django-marionettejs
=======================

django-marionette-js is a simple Django app to conduct Web-based django-marionettejs. For each
question, visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "django-marionettejs" to your INSTALLED_APPS setting like this::

.. code-block:: python

    INSTALLED_APPS = (
        'marionettejs',
    )

2. in yourtemplate, just extends 'base.html', you get a template with preconfigured backbone

3. or just include the fragment

.. code-block::html

   {% include 'marionettejs.html' %}
