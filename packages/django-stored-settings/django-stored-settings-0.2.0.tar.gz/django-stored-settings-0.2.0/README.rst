Django Stored Settings
======================

It often happens that we need to be able dynamically to create/edit some
settings and site variables, for example site title, logo and counter
code.

``stored-settings`` module is tailored specifically for these purposes
allowing dynamically to create and further on to edit via django-admin
records of the following types:

-  Char
-  Text
-  HTML text
-  Boolean
-  Image

Requirements
------------

Django stored-settings requires Django 1.3 or later and Pillow. Also has
TinyMCE integration.

Getting It
----------

You can get Django stored-settings by using pip or easy\_install:

``$ pip install stored-settings`` or ``$ easy_install stored-settings``

If you want to install it from source, grab the git repository from
GitHub and run setup.py:

::

    $ git clone git://github.com/zvadim/django-stored-settings.git
    $ cd stored_settings
    $ python setup.py install

Installing It
-------------

To enable ``stored-settings`` in your project you need to add it to
``INSTALLED_APPS`` in your projects ``settings.py`` file:

.. code:: python

    INSTALLED_APPS = (
        ...
        'stored_settings',
    )

And also add new content processor

.. code:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'stored_settings.context_processors.stored_settings',
    )

Last step is db migration

::

    $ python manage.py migrate 

Using It
--------

See an
`example <https://github.com/zvadim/django-stored-settings/tree/master/example>`__

TinyMCE
-------

For HTML fields TinyMCE can be applied. To enable ``TinyMCE`` support in
``stored-settings`` you need to add to ``settings.py`` the following:

.. code:: python


    STORED_SETTINGS_TINYMCE_ENABLE = True

