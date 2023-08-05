# -*- coding: utf-8 -*-
import os
import django

PROJECT_DIR = os.path.dirname(__file__)

TEST_PROJ = 'tests'
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'Fooooo'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

ROOT_URLCONF = TEST_PROJ + '.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'basic_email',
)

COVERAGE_EXCLUDE_MODULES = (
    "basic_email.migrations.*",
    "basic_email.tests*",
    "basic_email.urls",
    "basic_email.__init__",
)

COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = False
