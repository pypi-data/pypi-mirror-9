import os
import unittest
from optional_django.conf import Conf
from optional_django.env import DJANGO_INSTALLED, DJANGO_CONFIGURED, DJANGO_SETTINGS
from optional_django.exceptions import ConfigurationError
from optional_django.staticfiles import find
from optional_django import six


class TestConfUtilsDjangoIntegration(unittest.TestCase):
    def test_env_detection(self):
        self.assertTrue(DJANGO_INSTALLED)
        self.assertTrue(DJANGO_CONFIGURED)
        self.assertIsNotNone(DJANGO_SETTINGS)

    def test_namespaces_can_have_default_values_overridden(self):
        test_overrides = Conf('TEST_OVERRIDES', {
            'FOO': 'NOT-BAR',
            'BAR': 1,
        })
        self.assertEqual(test_overrides.FOO, 'BAR')
        self.assertEqual(test_overrides.BAR, 1)
        self.assertTrue(test_overrides._has_been_configured)
        self.assertTrue(test_overrides._configured_from_env)
        self.assertRaises(ConfigurationError, test_overrides.configure, {})

    def test_staticfiles_find_matches_relative_and_absolute_paths(self):
        abs_path = os.path.join(os.path.dirname(__file__), 'test_app', 'static', 'test.js')
        self.assertEqual(abs_path, find('test.js'))
        self.assertIsNone(find('test_app/static/test.js'))
        self.assertTrue(os.path.exists(abs_path))
        self.assertEqual(find(abs_path), abs_path)

    def test_six_is_accessible(self):
        self.assertTrue(six.PY2 or six.PY3)

    def test_vendored_six_is_not_django_vendored_version(self):
        from django.utils import six as django_six
        self.assertNotEqual(six, django_six)