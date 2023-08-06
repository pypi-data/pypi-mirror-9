django-mcmo
===========

|copyright| 2014-2015 Thomas Khyn

MCMO stands for 'Management Command Multiple Override'. This django app allows
multiple apps to override the same management command without evicting any.

Supports Django 1.4 to 1.8 and matching Python 2 and 3 versions.

Installation
------------

As straightforward as it can be, using pip::

   pip install django-mcmo

Usage
-----

In your ``manage.py`` file, replace the line::

    from django.core import management

by::

    from mcmo import management

You can now use applications that concurrently define overrides for
``django.core management`` commands. Both commands will be called.

For example, if you are using djinga_ and django-extra_keywords_, which
both override Django's ``makemessages`` management command, both commands from
both applications will be called subsequently.

The first command which will be called will be the one relative to the
application in the latest position in the ``INSTALLED_APPS``.


Alternative usage
-----------------

In  your manage.py is automatically generated (e.g. if you are using
buildout_ with djangorecipebook_ or djangorecipe_), simply make sure
that the statement::

    import mcmo

is executed before calling ``django.management.execute_from_command_line``.

Importing the package patches the ``django.core.management`` module, which
functions are then enabled for multiple-override support.


Limitations
-----------

The same-name overrides should all derive from the same command class, or at
least from on of Django's base command classes (``AppCommand``,
``LabelCommand`` or ``NoArgsCommand``).

``django-mcmo`` will raise a warning (but the execution will carry on) in case
of subclassing inconsistencies. For example, if the command ``cmd`` in ``app1``
inherits from ``AppCommand`` and the command ``cmd`` in ``app2`` inherits from
``NoArgsCommand``. Indeed, as only one command is likely to be executed in that
situation, the obtained results may not be consistent as it will depend on the
relative position of the apps in ``INSTALLED_APPS`` or raise an exception
regarding arguments presence, absence or type.

In practice, same-name commands will only be met when two 3rd party apps
override a Django core management command. They will therefore derive from the
same Command base class, and cause no issue in 99.9% of the cases.

``django-mcmo`` may also emit warning messages if the same option is
explicitly added in the same command of two distinct apps with command classes
not being subclasses of each other.


.. |copyright| unicode:: 0xA9
.. _djinga: https://pypi.python.org/pypi/djinga/
.. _django-extra_keywords: https://pypi.python.org/pypi/django-extra_keywords/
.. _buildout: https://pypi.python.org/pypi/zc.buildout/
.. _djangorecipebook: https://pypi.python.org/pypi/djangorecipebook/
.. _djangorecipe: https://pypi.python.org/pypi/djangorecipe/
