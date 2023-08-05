import unittest2

from appfy.recipe import utils


class TestOptionsUtils(unittest2.TestCase):

    def test_get_bool_for_true_values(self):
        true_values = (
            'TRUE',
            'True',
            'true',
            '1'
        )

        for true_value in true_values:
            self.assertTrue(utils.get_bool_option(true_value))

    def test_get_bool_for_false_values(self):
        false_values = (
            'FALSE',
            'False',
            'false',
            '0'
        )

        for false_value in false_values:
            self.assertFalse(utils.get_bool_option(false_value))
