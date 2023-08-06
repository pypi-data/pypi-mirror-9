=============
django-editos
=============

Django app to manage and display editos

Install
=======

Using PyPI::

    pip install django-editos

From source::

    python setup.py install

Testing
=======

Preparing test env::

    virtualenv ./virtualenv
    source virtualenv/bin/activate
    pip install django

Runing unit tests::

    python setup.py test

Configuring
===========

Add ``geelweb.django.editos`` to ``INSTALLED_APPS`` in your settings.

Create the db with ``python manage.py syncdb`` or ``python manage.py migrate editos``
if you are using `south <http://south.aeracode.org/>`_

Load the editos tags in your templates with ``{% load editos %}``

Edito model
===========

Fields
------

editos.models.Edito object have the following fields

**title**

Required. 100 characters or fewer.

**link**

Required. Url to redirect

**button_label**

Optional. 20 characters or fewer.

**image**

Required. Uploaded image.

**text_content**

Required. 400 characters or fewer.

**display_from**

Required. A date field to represent the date from which the item is active.

**display_until**

Required. A date field to represent the date by which the item is active.

**active**

Optional. Default to True. Define if the item is active.

**text_theme**

Required. A theme to apply to the item in the template rendering. Can be "light" or "dark". text_theme field use EDITOS_THEMES_ and EDITOS_DEFAULT_THEME_ settings.

Template tags
=============

**editos**

Render the editos. Example::

    {% editos 'path/to/a/template.html' %}

The first argument is the path to a template to use to render the editos. If
omited the default ``editos/carousel.html`` template is used.

Templates
=========

**editos/carousel.html**

The default template. Render a `Bootstrap 3 Carousel <http://getbootstrap.com/javascript/#carousel>`_

Write custom templates
======================

The editos will be assign to the template in the ``editos`` variable. Example::

    {% for edito in editos %}
      {{ edito.title }}
    {% endfor %}

Settings
========

.. _EDITOS_THEMES:

**EDITOS_THEMES**

Default::

    (
    ('light', 'Light'),
    ('dark', 'Dark'),
    )

A tuple of (value, label) choices

.. _EDITOS_DEFAULT_THEME:

**EDITOS_DEFAULT_THEME**

Default: "light"

The default theme to use

**EDITOS_HELP_TEXTS**

Default: {}

This sets the mapping of help text to model field. Example::

    EDITOS_HELP_TEXTS = {
        'image': '150 x 300px',
    }

License
=======

django-editos is released under MIT License. See LICENSE.txt file for details.

