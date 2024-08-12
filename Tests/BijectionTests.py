import unittest
import bijection


class TestBijection(unittest.TestCase):

    def test_creation(self):
        # Test successful creation of non-beta version
        created = bijection.Bijection()
        self.assertIsNotNone(created)


if __name__ == '__main__':
    unittest.main()
