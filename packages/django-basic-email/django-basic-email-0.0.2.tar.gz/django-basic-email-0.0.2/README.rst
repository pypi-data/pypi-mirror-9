==================
django-basic-email
==================

.. image:: https://pypip.in/version/django-basic-email/badge.svg
    :target: https://pypi.python.org/pypi/django-basic-email/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/django-basic-email/badge.svg
    :target: https://pypi.python.org/pypi/django-basic-email/
    :alt: Supported Python versions

.. image:: https://travis-ci.org/ArabellaTech/django-basic-email.svg
    :target: https://travis-ci.org/ArabellaTech/django-basic-email

.. image:: https://coveralls.io/repos/ArabellaTech/django-basic-email/badge.svg
    :target: https://coveralls.io/r/ArabellaTech/django-basic-email

.. image:: https://requires.io/github/ArabellaTech/django-basic-email/requirements.svg?branch=master
     :target: https://requires.io/github/ArabellaTech/django-basic-email/requirements/?branch=master
     :alt: Requirements Status

This Django Basic Email enable you to create emails in easy way.

This CMS is know to work on Django 1.4+ with Python 2.6+ and 3.3+

Instalation
===========

Get package or install by pip::

    pip install django-basic-email


Configuration
=============

Modify your ``settings.py``. Add ``'basic_email'`` to your
``INSTALLED_APPS`` like this:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'basic_email',
    )

Usage
=====

Create template ``emails/email_example.html`` and send email:

.. code-block:: python

    from basic_email.send import send_email
    send_email('example', 'joe@doe.com', 'Hello')

Options:
 - ``template`` template name from scheme ``emails/email_<name>.html``
 - ``email`` - receiver email
 - ``subject`` - subject email
 - ``variables`` - dict with variables to pass to template render
 - ``fail_silently`` - flag if error in sending email should raise (default ``False``)
 - ``replace_variables`` - dict with variables to replace in template
 - ``reply_to`` - reply_to header
 - ``attachments`` - attachments list (file objects)
 - ``memory_attachments`` - attachments list (string objects)


Testing
=======

1. Fork repository (if you don't have write permission).
2. Create a branch.
3. Add feature or fix a bug.
4. Push code.
5. Create a Pull Request.


Automated tests
---------------

Require Tox>=1.8

Testing all platforms

::

    tox

Testing one platforms

::

    tox -e <platform>

Example:

::

    tox -e py27-django-17

Testing interface
-----------------

1. Create virtual environment::

    # Preparing virtualenv paths (optional if your profile doesn't have it).
    export WORKON_HOME=~/Envs
    source /usr/bin/virtualenvwrapper_lazy.sh
    # or: source /usr/local/bin/virtualenvwrapper_lazy.sh

    # Start by creating a virtual environment using the helper scripts provided. Do not include the systems site-packages.
    mkvirtualenv django-basic-email --no-site-packages
    workon django-basic-email

2. Install ``django-basic-email`` in editable mode::

    pip install -e .

3. Run example project::

    cd example_project && ./manage.py migrate && ./manage.py runserver
