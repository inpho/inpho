import unittest2
from inpho.taxonomy import *

class TaxonomyTest(unittest2.TestCase):
    def test_pretty(self):
        filename = "inpho/tests/taxonomy.txt"
        tree = from_pretty(filename)
        with open(filename) as f:
            self.assertEqual(f.read().strip(), '\n'.join(tree.pretty()))

    def test_graft(self):
        root = Node("root")
        child = Node("child")
        root.graft(child)
        self.assertIn(child, root)

    def test_prune(self):
        root = Node("root")
        child = Node("child")
        root.graft(child)

        value = root.prune(child)
        
        # test success
        self.assertNotIn(child, root)

        # test return value
        self.assertEqual(value, child)

        # test KeyError
        with self.assertRaises(KeyError):
            root.prune(child)

    def test_fragment(self):
        root = Node("root")
        child = Node("child")
        root.graft(child)

        value = child.fragment()
        
        # test success
        self.assertNotIn(child, root)

        # test return value
        self.assertEqual(value, child)

        # test KeyError
        with self.assertRaises(KeyError):
            root.prune(child)

    def test_siblings(self):
        root = Node("root")
        child = Node("child")
        child2 = Node("child2")
        root.graft(child)
        root.graft(child2)

        self.assertIn(child, child2.siblings)
        self.assertIn(child2, child.siblings)
        self.assertNotIn(child, child.siblings)
        self.assertNotIn(child2, child2.siblings) 

    def test_search(self):
        root = Node("root")
        child = Node("child")
        child2 = Node("grandchild")
        root.graft(child)
        child.graft(child2)

        # test direct descendant search
        value = root.search("child")
        self.assertEqual(value, child)

        # test granddescendant 
        value = root.search("grandchild")
        self.assertEqual(value, child2)

        # test parent does not occur
        value = child.search("root")
        self.assertFalse(value)


    def test_path(self):
        pass

    def test_path_to(self):
        pass

if __name__ == '__main__':
   suite = unittest2.TestLoader().loadTestsFromTestCase(TaxonomyTest)
   unittest2.TextTestRunner(verbosity=2).run(suite)
