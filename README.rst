.. image:: https://img.shields.io/pypi/v/django-slick-reporting.svg
    :target: https://pypi.org/project/django-slick-reporting

.. image:: https://img.shields.io/pypi/pyversions/django-slick-reporting.svg
    :target: https://pypi.org/project/django-slick-reporting

.. image:: https://img.shields.io/readthedocs/django-slick-reporting
    :target: https://django-slick-reporting.readthedocs.io/

.. image:: https://api.travis-ci.com/ra-systems/django-slick-reporting.svg?branch=master
    :target: https://app.travis-ci.com/github/ra-systems/django-slick-reporting

.. image:: https://img.shields.io/codecov/c/github/ra-systems/django-slick-reporting
    :target: https://codecov.io/gh/ra-systems/django-slick-reporting



Django-admin-commands
=====================

Sometimes one would like to allow the admin to have access to some of the management commands.
djagno-admin-commands2 is the answer. A Tool to execute management commands from admin with ease and control.


Features
--------

* Specify the commands you need to allow for admin to execute. (Or explicitly choose all)
* Get the logs out in admin
* Easily customizable to use django-rq or other queueing technique


Installation
------------
* Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install django-admin-commands2.
  *There was a package with the same name on pypi , hence the 2 suffix*

.. code-block:: console

        pip install django-admin-commands2

* Add admin_commands to you INSTALLED_APPS

* migrate



Usage
-----
* Adds the commands you need to allow to the admin

.. code-block:: python

        ADMIN_COMMANDS_CONFIG = {
                'allowed_commands': ['ping_google', 'update_index']
        }

* Navigate to the admin site `/admin_commands/managementcommands/` to find the