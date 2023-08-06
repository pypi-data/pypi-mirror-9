#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691"""
import sys

from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings

import dj_database_url


settings.configure(
    DATABASES={
        'default': dj_database_url.config(default='postgres://localhost/feincms_extensions'),
    },
    DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
    INSTALLED_APPS=(
        # Put contenttypes before auth to work around test issue.
        # See: https://code.djangoproject.com/ticket/10827#comment:12
        'django.contrib.sites',
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',

        'feincms',
        'feincms.module.medialibrary',
        'feincms.module.page',

        'feincms_extensions',
        'feincms_extensions.tests',

        'mptt',
    ),
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',),
    ROOT_URLCONF='feincms_extensions.tests.urls',
    SITE_ID = 1,
    MIDDLEWARE_CLASSES = (),
    TEMPLATE_CONTEXT_PROCESSORS = (
        'feincms.context_processors.add_page_if_missing',
    ),
)

import django
if django.VERSION >= (1, 7):
    django.setup()

from django.test.runner import DiscoverRunner


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    pass


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['feincms_extensions'])
if failures:
    sys.exit(1)
