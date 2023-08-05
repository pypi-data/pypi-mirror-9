# -*- coding: utf-8 -*-

import unittest

from ..fields import ConstantDict

class ConstDemo(ConstantDict):
    TEST = "OK"

class TestMessage(unittest.TestCase):
    def setUp(self):
        pass

    def test_custom_field_getattr(self):
        consttest = ConstDemo()
        self.assertEqual(getattr(consttest, "TEST"), "OK")

    def test_custom_field_missing_getattr(self):
        consttest = ConstDemo()
        try:
            getattr(consttest, "NOTTHERE")
        except AttributeError:
            assert(True)
        else:
            assert(False)


    def test_regular_getattr(self):
        consttest = ConstDemo()
        self.assertIsNotNone(getattr(consttest, "dict"))

    def test_regular_getattr_failure(self):
        consttest = ConstDemo()
        try:
            getattr(consttest, "nowwayxxx")
        except AttributeError:
            assert(True)
        else:
            assert(False)
