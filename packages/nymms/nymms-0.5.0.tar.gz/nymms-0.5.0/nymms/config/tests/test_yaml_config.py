import unittest
import os

from nymms.config import yaml_config


class TestIncludeLoader(unittest.TestCase):
    def setUp(self):
        self.root = os.path.dirname(__file__)

    def test_relative_include(self):
        full_path = os.path.join(self.root, 'config.yaml')
        version, relative_config = yaml_config.load_config(full_path)
        self.assertEqual(relative_config['foo'], 'bar')
        self.assertEqual(relative_config['file1'], 1)

    def test_missing_config(self):
        with self.assertRaises(IOError):
            yaml_config.load_config('nonexistant.yaml')

    def test_indent_include(self):
        full_path = os.path.join(self.root, 'config.yaml')
        version, relative_config = yaml_config.load_config(full_path)
        self.assertEqual(relative_config['included']['a'], 1)

    def test_empty_config(self):
        full_path = os.path.join(self.root, 'empty.yaml')
        with self.assertRaises(yaml_config.EmptyConfig) as ee:
            yaml_config.load_config(full_path)
        self.assertEqual(ee.exception.filename, full_path)
