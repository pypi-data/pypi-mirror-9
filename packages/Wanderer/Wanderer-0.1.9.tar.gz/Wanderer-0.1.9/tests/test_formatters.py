# -*- coding: utf-8 -*-

import re
import unittest
from fnmatch import fnmatch
from wanderer.formatters import format_regex, format_glob, format_partial

template = ('assets/{asset.type}/{asset.name}/{stage.name}/maya/work/'
            '{stage.short}_{asset.name}.v{version:0>3d}.mb')
test_path = 'assets/character/asset_a/model/maya/work/mdl_asset_a.v002.mb'


class TestRegexFormatter(unittest.TestCase):

    def test_format(self):
        '''Ensure Regexer is returning the correct string'''

        expected = ('assets/(?P<asset_type>.*?)/(?P<asset_name>.*?)/'
                    '(?P<stage_name>.*?)/maya/work/(?P<stage_short>.*?)'
                    '_(?:.*?).v(?P<version>.*?).mb')
        self.assertEqual(format_regex(template), expected)

    def test_regex(self):
        '''Ensure Regexer formatted string is a valid regex pattern'''

        expected_data = {
            'asset_name': 'asset_a',
            'asset_type': 'character',
            'stage_name': 'model',
            'stage_short': 'mdl',
            'version': '002'
        }
        pattern = re.compile(format_regex(template))
        data = pattern.search(test_path).groupdict()
        self.assertEqual(data, expected_data)


class TestGlobFormatter(unittest.TestCase):

    def test_format(self):
        '''Ensure globber is returning the expected string'''

        expected = 'assets/*/*/*/maya/work/*_*.v*.mb'
        formatted = format_glob(template)
        self.assertEqual(formatted, expected)

    def test_fnmatch(self):
        '''Ensure Globber formatted template works with fnmatch'''

        pattern = format_glob(template)
        self.assertTrue(fnmatch(test_path, pattern))


class TestPartialFormatter(unittest.TestCase):

    def setUp(self):
        self.template = 'assets/{asset}/{typ}/work/{asset}.v{v:0>3d}.mb'

    def test_format(self):
        '''Ensure normal formatting works'''

        data = {
            'asset': 'asset_a',
            'typ': 'model',
            'v': 4,}
        expected = 'assets/asset_a/model/work/asset_a.v004.mb'

        formatted = format_partial(self.template, **data)
        self.assertEqual(formatted, expected)

    def test_partial(self):
        '''Ensure partial formatting works'''

        partial_data = {'asset': 'asset_a'}
        expected = 'assets/asset_a/{typ}/work/asset_a.v{v:0>3d}.mb'

        formatted = format_partial(self.template, **partial_data)
        self.assertEqual(formatted, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
