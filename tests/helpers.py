import unittest2
import inpho.helpers

class TestUrlFuction(unittest2.TestCase):

    def SetUp(self):
        pass

    def tearDown(self):
        pass

    def test_url(self):
        self.assertEqual(inpho.helpers.url("entity"), 
                         "/entity")
        self.assertEqual(inpho.helpers.url("idea", 646), 
                         "/idea/646")
        self.assertEqual(inpho.helpers.url("idea", 737, "graph"), 
                         "/idea/737/graph")
        self.assertEqual(inpho.helpers.url("thinker", 3919, "search_with", 
                                           3724), 
                         "/thinker/3919/search_with/3724")
        self.assertEqual(inpho.helpers.url("work", 5413, filetype="json"), 
                         "/work/5413.json")
        self.assertRaises(inpho.helpers.ArgumentError, inpho.helpers.url, 
                          "journal", 4205, id2=4206)
        self.assertRaises(inpho.helpers.ArgumentError, inpho.helpers.url, 
                          "school_of_thought", action="related", id2=5390)

if __name__ == '__main__':
    unittest2.main()
