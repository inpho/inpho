import unittest2 as unittest
from inpho.model import Date


class DateTestFunctions(unittest.TestCase):
    def setUp(self):
        self.date = Date(646, 2, 2012, 4, 17)

    def test_identity(self):
        self.assertEqual(self.date, self.date)
        
        date2 = Date(646, 2, 2012, 4, 17)
        self.assertEqual(self.date, date2)

    def test_repr_identity(self):
        date2 = Date.convert_from_iso(646, 2, repr(self.date))
        self.assertEqual(repr(self.date), repr(date2))

if __name__ == '__main__':
    unittest.main()
