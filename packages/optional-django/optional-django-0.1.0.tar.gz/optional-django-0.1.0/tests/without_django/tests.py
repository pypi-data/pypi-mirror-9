import os
import unittest
from optional_django.conf import Conf
from optional_django.exceptions import ConfigurationError
from optional_django.staticfiles import find
from optional_django.env import DJANGO_INSTALLED, DJANGO_CONFIGURED, DJANGO_SETTINGS
from optional_django import six


class TestOptionalDjangoWithoutDjango(unittest.TestCase):
    def test_env_detection(self):
        self.assertTrue(DJANGO_INSTALLED)
        self.assertFalse(DJANGO_CONFIGURED)
        self.assertIsNone(DJANGO_SETTINGS)

    def test_basic_conf_instance(self):
        test_conf = Conf('test_conf', {
            'TEST_SETTING_1': 1,
            'TEST_SETTING_2': {
                'FOO': 'BAR'
            }
        })
        self.assertEqual(test_conf.TEST_SETTING_1, 1)
        self.assertEqual(test_conf.TEST_SETTING_2, {'FOO': 'BAR'})

    def test_conf_instance_can_be_configured_at_runtime(self):
        test_conf = Conf('test_conf', {})
        self.assertEqual(test_conf.get('TEST_SETTING_1', None), None)
        self.assertEqual(test_conf.get('TEST_SETTING_2', None), None)
        test_conf.configure({
            'TEST_SETTING_1': 1,
            'TEST_SETTING_2': {
                'FOO': 'BAR'
            }
        })
        self.assertEqual(test_conf.get('TEST_SETTING_1', None), 1)
        self.assertEqual(test_conf.get('TEST_SETTING_2', None), {'FOO': 'BAR'})
        self.assertTrue(test_conf._has_been_configured)
        self.assertFalse(test_conf._configured_from_env)
        self.assertRaises(ConfigurationError, test_conf.configure, {})

    def test_staticfiles_find_only_matches_absolute_paths(self):
        self.assertIsNone(find('test.js'))
        self.assertIsNone(find('test_app/static/test.js'))
        abs_path = os.path.join(os.path.dirname(__file__), 'test_app', 'static', 'test.js')
        self.assertTrue(os.path.exists(abs_path))
        self.assertEqual(find(abs_path), abs_path)

    def test_six_is_accessible(self):
        self.assertTrue(six.PY2 or six.PY3)