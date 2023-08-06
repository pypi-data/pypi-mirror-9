import unittest

from smarttest.decorators import test_type

class SomeAcceptanceTestCase(unittest.TestCase):
    """ Test method. """

    def setUp(self):
        super(SomeAcceptanceTestCase, self).setUp()
        self.mocker = Mocker()

    def tearDown(self):
        super(SomeAcceptanceTestCase, self).tearDown()

    def test_should_name(self):
        """ Scenariusz: Opis scenariusza """
        # Zakładając,
        # Jeżeli,
        self.mocker.replay()
        try:
            result = method(params)
        finally:
            self.mocker.restore()
        # Wtedy
        self.mocker.verify()

