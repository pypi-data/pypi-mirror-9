from unittest import TestCase
from condorpy import Job, DAG, Node, Templates
import os

__author__ = 'sdc50'


class TestTemplates(TestCase):

    def setUp(self):
        Templates.reset()
        self.default_save_location = os.path.join(os.path.dirname(__file__), '../condorpy/condorpy-saved-templates')
        self.custom_save_location = 'saved-templates'

    def tearDown(self):
        for file in (self.custom_save_location, self.default_save_location):
            if os.path.isfile(file):
                os.remove(file)

    def test__init__(self):
        pass

    def test__str__(self):
        pass

    def test__repr__(self):
        pass

    def test___getattribute__(self):
        custom = dict(key='value')
        Templates.custom = custom
        new = Templates.custom
        self.assertIsNot(custom, new)

    def test_save(self):
        file_name = self.default_save_location
        Templates.save()
        f = open(file_name)
        expected = "(dp0\n."
        actual = f.read()
        msg = 'testing saving with empty dict'
        self.assertEqual(expected, actual, '%s\nExpected: %s\nActual:   %s\n' % (msg, expected, actual))

        file_name = self.custom_save_location
        Templates.save(file_name)
        f = open(file_name)
        expected = "(dp0\n."
        actual = f.read()
        msg = 'testing saving with empty dict to custom location'
        self.assertEqual(expected, actual, '%s\nExpected: %s\nActual:   %s\n' % (msg, expected, actual))

        file_name = self.default_save_location
        self.test___getattribute__()
        Templates.save()
        f = open(file_name)
        expected = "(dp0\nS'custom'\np1\n(dp2\nS'key'\np3\nS'value'\np4\nss."
        actual = f.read()
        msg = 'testing saving with custom template added'
        self.assertEqual(expected, actual, '%s\nExpected: %s\nActual:   %s\n' % (msg, expected, actual))

    def test_load(self):
        self.test___getattribute__()
        Templates.save()
        expected = Templates.__dict__
        Templates.reset()
        Templates.load()
        actual = Templates.__dict__
        msg = 'testing loading with custom template added'
        self.assertEqual(expected, actual, '%s\nExpected: %s\nActual:   %s\n' % (msg, expected, actual))
