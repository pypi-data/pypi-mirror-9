#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import click
import importlib

from django import VERSION
from django.conf import settings as django_settings
from django.test.utils import get_runner


@click.command()
@click.option('--settings', default='test_settings', help='Test settings module.')
@click.option('--failfast', default=False)
def runtests(settings, failfast):
    if VERSION[0] == 1 and VERSION[1] < 6:
        runner = 'django.test.simple.DjangoTestSuiteRunner'
    else:
        runner = 'django.test.runner.DiscoverRunner'
    test_settings = {}
    mod = importlib.import_module(settings)
    for setting in dir(mod):
        if setting.isupper():
            test_settings[setting] = getattr(mod, setting)
    test_settings['TEST_RUNNER'] = runner
    django_settings.configure(**test_settings)
    if VERSION[1] >= 7:
        from django import setup
        setup()
    test_runner = get_runner(django_settings)(verbosity=1, interactive=False, failfast=failfast)
    failures = test_runner.run_tests(test_settings['INSTALLED_APPS'])
    return failures

if __name__ == "__main__":
    failures = runtests()
    sys.exit(failures)
