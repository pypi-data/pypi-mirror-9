# -*- coding: utf-8 -*-
import os

abspath = lambda *p: os.path.abspath(os.path.join(*p))

PROJECT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = abspath(os.path.dirname(__file__))

SITE_ID = 1
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': abspath(PROJECT_ROOT, '.hidden.db'),
        'TEST_NAME': ':memory:',
    },
}

SECRET_KEY = 'CHANGE_THIS_TO_SOMETHING_UNIQUE_AND_SECURE'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'basic_email',
    'tests',
)


STATIC_URL = '/static/'

COVERAGE_EXCLUDE_MODULES = (
    "basic_email.migrations.*",
    "basic_email.tests*",
    "basic_email.urls",
    "basic_email.__init__",
)

COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = False
