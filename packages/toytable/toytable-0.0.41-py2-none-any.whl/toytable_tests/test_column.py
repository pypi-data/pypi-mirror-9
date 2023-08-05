import array
import unittest
from toytable.columns import Column, ArrayColumn


class TestColumn(unittest.TestCase):

    def test_column(self):
        """A column can be constructed with no data."""
        c = Column('foo')
        self.assertEqual(list(c), [])

    def test_column_data(self):
        """A column can be constructed with initial data."""
        c = Column('foo', range(3))
        self.assertEqual(list(c), [0, 1, 2])

    def test_column_index(self):
        """A column can be indexed, just like a list."""
        c = Column('foo', range(3))
        self.assertEqual(c[0], 0)
        self.assertEqual(c[1], 1)
        self.assertEqual(c[2], 2)

    def test_column_index_out_of_bounds(self):
        """A column can be indexed, and throws an IndexError if out of bounds."""
        c = Column('foo', range(3))
        with self.assertRaises(IndexError):
            c[4]

    def test_column_negative_index(self):
        """A column can be negativly indexed."""
        c = Column('foo', range(3))
        self.assertEqual(c[-1], 2)
        self.assertEqual(c[-2], 1)
        self.assertEqual(c[-3], 0)

    def test_column_type(self):
        """A column can be constructed specifying a type."""
        c = Column('foo', range(3), type=int)
        self.assertEqual(list(c), [0, 1, 2])


if __name__ == '__main__':
    unittest.main()
