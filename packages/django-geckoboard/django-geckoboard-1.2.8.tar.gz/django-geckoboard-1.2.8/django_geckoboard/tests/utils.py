"""
Testing utilities.
"""

from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test.utils import get_runner, setup_test_environment
from django.test.testcases import TestCase as DjangoTestCase


def run_tests(labels=()):
    """
    Use the Django test runner to run the tests.
    """
    setup_test_environment()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    return test_runner.run_tests(None)


class TestCase(DjangoTestCase):
    """
    Base test case for the django-analytical tests.

    Includes the settings manager.
    """

    def setUp(self):
        self.settings_manager = TestSettingsManager()

    def tearDown(self):
        self.settings_manager.revert()


class TestSettingsManager(object):
    """
    From: http://www.djangosnippets.org/snippets/1011/

    A class which can modify some Django settings temporarily for a
    test and then revert them to their original values later.

    Automatically handles resyncing the DB if INSTALLED_APPS is
    modified.
    """

    NO_SETTING = ('!', None)

    def __init__(self):
        self._original_settings = {}

    def set(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._original_settings.setdefault(k, getattr(settings, k,
                    self.NO_SETTING))
            setattr(settings, k, v)
        if 'INSTALLED_APPS' in kwargs:
            self.syncdb()

    def delete(self, *args):
        for k in args:
            try:
                self._original_settings.setdefault(k, getattr(settings, k,
                        self.NO_SETTING))
                delattr(settings, k)
            except AttributeError:
                pass  # setting did not exist

    def syncdb(self):
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0, interactive=False)

    def revert(self):
        for k,v in self._original_settings.iteritems():
            if v == self.NO_SETTING:
                if hasattr(settings, k):
                    delattr(settings, k)
            else:
                setattr(settings, k, v)
        if 'INSTALLED_APPS' in self._original_settings:
            self.syncdb()
        self._original_settings = {}
