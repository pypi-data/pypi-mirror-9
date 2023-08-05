# -*- coding: utf-8 -*-

import wanderer
import unittest


class TestAppTemplate(unittest.TestCase):

    def setUp(self):
        self.app = wanderer.Wanderer()

    def tearDown(self):
        pass

    def test_default_config(self):
        expected_config = {
            'debug': False,
        }

        assert self.app.config == expected_config

if __name__ == '__main__':
    unittest.main()
