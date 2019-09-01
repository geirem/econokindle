import unittest
from econokindle.KeyCreator import KeyCreator


class KeyCreatorTest(unittest.TestCase):

    def test_that_prefixes_are_prepended(self):
        expected = 'foo'
        key_creator = KeyCreator(expected)
        self.assertTrue(key_creator.key('bar').startswith(expected))

    def test_that_keys_ends_with_name(self):
        expected = 'thisname'
        key_creator = KeyCreator('foo')
        self.assertTrue(key_creator.key(expected).endswith(expected))

    def test_that_keys_are_prefix_underscore_and_name(self):
        prefix = 'foo'
        name = 'bar'
        key_creator = KeyCreator(prefix)
        self.assertEqual(prefix + '_' + name, key_creator.key(name))
