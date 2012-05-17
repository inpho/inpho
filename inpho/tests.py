import unittest2
import httplib
import inpho.corpus.sep as sep
from inpho.model import *
import sqlalchemy

__all__ = ["Autotest"]

class Autotest(unittest2.TestCase):
    def getPassedTests(self):
        return passed

    def setUp(self):
        self.conn = httplib.HTTPConnection("inphodev.cogs.indiana.edu:8087")

    def test_sep_crossRef(self):
        """
        SEP Cross-References
        Verify that SEP Cross-Reference at http://plato.stanford.edu/~inpho/crossref.php still works
        http://plato.stanford.edu/~inpho/crossref.php
        """
        self.conn = httplib.HTTPConnection("plato.stanford.edu")
        self.conn.request("GET", "/~inpho/crossref.php")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 200)
        
    def test_entity_json(self):
        """
        Entity JSON
        Verify that https://inpho.cogs.indiana.edu/entity.json returns HTTP 200
        https://inpho.cogs.indiana.edu/entity.json
        """
        self.conn.request("GET", "/entity")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_idea_json(self):
        """
        Idea JSON
        Verify that https://inpho.cogs.indiana.edu/idea.json returns HTTP 200
        https://inpho.cogs.indiana.edu/idea.json
        """
        self.conn.request("GET", "/idea")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_thinker_json(self):
        """
        Thinker JSON
        Verify that https://inpho.cogs.indiana.edu/thinker.json returns HTTP 200
        https://inpho.cogs.indiana.edu/thinker.json
        """
        self.conn.request("GET", "/thinker")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_journal_json(self):
        """
        Journal JSON
        Verify that https://inpho.cogs.indiana.edu/journal.json returns HTTP 200
        https://inpho.cogs.indiana.edu/journal.json
        """
        self.conn.request("GET", "/journal")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_taxonomy_json(self):
        """
        Taxonomy JSON
        Verify that https://inpho.cogs.indiana.edu/taxonomy.json returns HTTP 200
        https://inpho.cogs.indiana.edu/taxonomy.json
        """
        self.conn.request("GET", "/taxonomy")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_search_box(self):
        """
        Search Box
        Verify autocomplete works. Easy test: "time"
        https://inpho.cogs.indiana.edu/entity.json?q=time
        """
        self.conn.request("GET", "/entity.json?q=time")
        result = self.conn.getresponse()
        data = result.read()
        # blank result returns data with length 84
        # checks to see if the search returns at least one result
        self.assertGreater(len(data), 84)

    def test_owl(self):
        """
        OWL
        Verify log-generating script works
        https://inpho.cogs.indiana.edu/owl
        """
        #OWL script
        node_q = Session.query(Node)
        thinker_q = Session.query(Thinker)
        profession_q = Session.query(Profession)
        nationality_q = Session.query(Nationality)
        
        nodes = node_q.all()
        thinkers = thinker_q.all()
        professions = profession_q.all()
        nationalities = nationality_q.all()
        
        # Compare length of lists to expected lengths
        self.assertGreaterEqual(len(nodes), 275)
        self.assertGreaterEqual(len(thinkers), 1758)
        self.assertGreaterEqual(len(professions), 906)
        self.assertGreaterEqual(len(nationalities), 86)


    def test_ui_eval(self):
        """
        Evaluation UI
        Verify user is able to Enable evaluations, choose an item, choose a setting, and submit an evaluation.
        http://inpho.cogs.indiana.edu/idea/1488
        """
        #make user eval using POST
        #look for develper tools (use google chrome or new firefox)
        self.conn.request("POST", "/idea/1488/relatedness/1793")
        r_result = self.conn.getresponse()
        self.conn.request("POST", "/idea/1488/generality/1793")
        g_result = self.conn.getresponse()
        self.assertLessEqual(r_result.status, 400)
        self.assertLessEqual(g_result.status, 400)

    def test_database_eval(self):
        """
        Evaluation Database
        Verify evaluation submissions append to database
        http://inpho.cogs.indiana.edu/idea/1488
        """
        #being able to delete user eval
        self.conn.request("GET", "/idea/1488/relatedness/1793?_method=DELETE")
        r_result = self.conn.getresponse()
        self.conn.request("GET", "/idea/1488/generality/1793?_method=DELETE")
        g_result = self.conn.getresponse()
        #FAILING because both status variables return 302 'FOUND', NOT 400
        self.assertLessEqual(r_result.status, 400)
        self.assertLessEqual(g_result.status, 400)
        
    def test_sep_publishing_list(self):
        """
        SEP Publishing list
        Verify items are not already in database. Check sep_dir fields.
        https://inpho.cogs.indiana.edu/admin
        """
        new = sep.new_entries()
        entries_in_db = 0
        for entry in new:
            if(len(Session.query(Entity).filter(Entity.sep_dir == entry).all()) > 0):
                entries_in_db += 1
                print entry
        self.assertEqual(entries_in_db, 0)

if __name__ == '__main__':
   suite = unittest2.TestLoader().loadTestsFromTestCase(Autotest)
   unittest2.TextTestRunner(verbosity=2).run(suite)
