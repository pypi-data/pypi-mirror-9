The Cut Duration Field
======================

This app provides a custom Django model field, ``RelativeDeltaField``, and
related form fields and widgets. ``RelativeDeltaField`` stores time durations
using `ISO 8601`_ representations, and returns ``dateutil.relativedelta``
objects which may be used directly with ``datetime.datetime`` objects.

This project was inspired by packages such as `django-durationfield`_. However,
this project focuses on:

#. providing a database-agnostic, standards-compliant way of storing the
   durations in the database (using `ISO 8601`_).
#. returning ``dateutil.relativedelta`` objects that can be used to perform
   calculations on ``datetime.datetime`` objects.

Note that `django-durationfield`_ provides the ability to filter querysets
based on the relative size of the stored duration, which is not possible with
this project. I.e., you can't use ``__lt`` and ``__gt`` etc., when filtering
by fields provided by this project.


Usage
-----


Model field
~~~~~~~~~~~

.. code:: python

    from django.db import models
    from datetime import datetime
    from thecut.durationfield.models import RelativeDeltaField


    class MyModel(models.Model):
        duration = RelativeDeltaField(blank=True, null=True)


    my_instance = MyModel(duration='P7D')
    datetime(2014, 1, 1) + my_instance.duration  # datetime(2014, 1, 8, 0, 0)


Form field
~~~~~~~~~~

Two form fields are provided: ``RelativeDeltaChoiceField`` and
``RelativeDeltaTextInput``:

.. code:: python

    from django import forms
    from thecut.durationfield.models import RelativeDeltaChoiceField

    DURATIONS = [
        ('', 'Never'),
	('P7D', 'One week'),
	('P1M', 'One month'),
    ]

    class MyForm(forms.ModelForm):

        duration = RelativeDeltaChoiceField(choices=DURATIONS)


or, if you'd prefer to type in the (`ISO 8601`_ compliant) value manually:

.. code:: python

    from django import forms
    from thecut.durationfield.forms import RelativeDeltaTextInput

    class MyForm(forms.ModelForm):

        duration = RelativeDeltaTextInput()


Installation
------------

#. Install from `pypi`_ using `pip`_:

   .. code:: sh

     pip install thecut-durationfield

#. Add ``thecut.durationfield`` to your ``settings.INSTALLED_APPS``:

   .. code:: python

    INSTALLED_APPS = (
        ...
	'thecut.durationfield',
	...
    )


Running the tests
-----------------

Assuming you've checked out the code into a directory called
``thecut-durationfield``, start by setting up your virtualenv:

.. code:: sh

  $ cd thecut-durationfield
  $ virtualenv . --no-site-packages
  $ source bin/activate
  (thecut-durationfield)$ pip install -r requirements-test.txt


and run the tests:

.. code:: sh

  (thecut-durationfield)$ python runtests.py


Alternatively, you can run the tests across all supported versions of Python
and Django with tox. After setting up and activating your virtualenv, install
and run tox:

.. code:: sh

  (thecut-durationfield)$ pip install tox
  (thecut-durationfield)$ tox


.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601#Durations
.. _`django-durationfield`: https://github.com/johnpaulett/django-durationfield
.. _`pypi`: http://pypi.python.org/pypi/django-timezone-field/
.. _`pip`: http://www.pip-installer.org/

CHANGES
=======


1.0.6 (2014-07-28)
------------------

* Fix an issue which caused an empty ``relativedelta`` to be returned for a
  database NULL value.
* Get ``tox`` up and running.
* Update package for public release.


1.0.5 (2014-03-19)
------------------

- Remove ``distribute`` from ``install_requires``.


1.0.4 (2013-12-17)
-------------------

- Fixed an issue with Postgres's fixed-length 64 character field.


1.0.3 (2013-09-28)
------------------

- Minor code cleanup.


1.0.2 (20132-08-08)
-------------------

- Add a Select widget for friendlier form input.


1.0.1 (2013-07-25)
------------------

- Fixes to south introspection rules.


1.0 (2013-07-25)
----------------

- First useful release with base model and form fields.


0.1 (2013-06-10)
----------------

- Initial release, mostly useless.


