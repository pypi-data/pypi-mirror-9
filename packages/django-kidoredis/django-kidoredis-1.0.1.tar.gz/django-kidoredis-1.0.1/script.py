import unittest

from smarttest.decorators import test_type


@test_type('acceptance')
class SomeAcceptanceTestCase(unittest.TestCase):

    def test_some_acceptance_test(self):
        pass


@test_type('unit')
class SomeUnitTestCase(unittest.TestCase):

    def test_some_unit_test(self):
        pass


class UnspecifiedTypeTestCase(unittest.TestCase):

    def test_some_test(self):
        pass
