import unittest2
from inpho.taxonomy import *

class TaxonomyTest(unittest2.TestCase):
    def test_pretty(self):
        filename = "inpho/tests/taxonomy.txt"
        tree = from_pretty(filename)
        with open(filename) as f:
            self.assertEqual(f.read().strip(), '\n'.join(tree.pretty()))

if __name__ == '__main__':
   suite = unittest2.TestLoader().loadTestsFromTestCase(TaxonomyTest)
   unittest2.TextTestRunner(verbosity=2).run(suite)
