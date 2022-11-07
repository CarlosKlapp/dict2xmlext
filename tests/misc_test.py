import unittest
from libs.misc import coalesce


class TestMisc(unittest.TestCase):

    def test_coalesce(self):
        self.assertIsNone(coalesce())
        self.assertIsNone(coalesce(None))
        self.assertIsNone(coalesce(None, None))
        self.assertIsNone(coalesce(None, None, None))
        self.assertEqual('a', coalesce('a', 'b', 'c'))
        self.assertEqual('a', coalesce('a', 'b', None))
        self.assertEqual('a', coalesce('a', None, 'c'))
        self.assertEqual('a', coalesce('a', None, None))
        self.assertEqual('b', coalesce(None, 'b', 'c'))
        self.assertEqual('b', coalesce(None, 'b', None))
        self.assertEqual('c', coalesce(None, None, 'c'))
        self.assertEqual(5, coalesce(5, 'g'))
        self.assertEqual('g', coalesce('g', 5))


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
