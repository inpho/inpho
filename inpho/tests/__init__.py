import unittest2
import httplib
import inpho.corpus.sep as sep
from inpho.model import *
import sqlalchemy

__all__ = ["Autotest"]

class Autotest(unittest2.TestCase):
    # Each test function's docstring should be written in this format:
    # TITLE
    # DESCRIPTION (including URL that is being tested) 
    #
    # * The url should only be complete if it is not on the local server (your test server). Otherwise,
    # it should just be the path after the server host in the url.
    def __init__(self, methodName='runTest', host='inphodev.cogs.indiana.edu:8087'):
        """
        Override of init to allow for a parameter for the inpho host.
        """
        super(Autotest, self).__init__(methodName)
        self.host = host

    def getPassedTests(self):
        return passed

    def setUp(self):
        self.conn = httplib.HTTPConnection(self.host)

    def test_sep_crossRef(self):
        """
        SEP Cross-References
        Verify that SEP Cross-Reference at http://plato.stanford.edu/~inpho/crossref.php still works
        """
        self.conn = httplib.HTTPConnection("plato.stanford.edu")
        self.conn.request("GET", "/~inpho/crossref.php")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 200)
        
    def test_entity_json(self):
        """
        Entity JSON
        Verify that /entity.json returns HTTP 200
        """
        self.conn.request("GET", "/entity.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_json(self):
        """
        Idea JSON
        Verify that /idea.json returns HTTP 200
        """
        self.conn.request("GET", "/idea.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_first_order_json(self):
        """
        Idea First-Order JSON
        Verify that https://inpho.cogs.indiana.edu/idea/646/first_order.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646/first_order.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_occurrences_json(self):
        """
        Idea Occurrences JSON
        Verify that https://inpho.cogs.indiana.edu/idea/646/occurrences.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646/occurrences.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_related_json(self):
        """
        Idea Related JSON
        Verify that https://inpho.cogs.indiana.edu/idea/646/related.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646/related.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_hyponyms_json(self):
        """
        Idea Hyponyms JSON
        Verify that https://inpho.cogs.indiana.edu/idea/646/hyponyms.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646/hyponyms.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)
    
    def test_idea_evaluated_json(self):
        """
        Idea evaluated JSON
        Verify that https://inpho.cogs.indiana.edu/idea/646/evaluated.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646/evaluated.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_thinker_json(self):
        """
        Thinker JSON
        Verify that /thinker.json returns HTTP 200
        """
        self.conn.request("GET", "/thinker.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_specific_entity_json(self):
        """
        Specific Entity JSON
        Verify that /entity/646.json returns HTTP 200
        """
        self.conn.request("GET", "/entity/646.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_specific_thinker_json(self):
        """
        Specific Thinker JSON
        Verify that /thinker/3724.json returns HTTP 200
        """
        self.conn.request("GET", "/thinker/3724.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_specific_idea_json(self):
        """
        Specific Idea JSON
        Verify that /idea/646.json returns HTTP 200
        """
        self.conn.request("GET", "/idea/646.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_specific_school_of_thought_json(self):
        """
        Specific School of Thought JSON
        Verify that /school_of_thought/5433.json returns HTTP 200
        """
        self.conn.request("GET", "/school_of_thought/5433.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_specific_work_json(self):
        """
        Specific Work JSON
        Verify that /work/5416.json returns HTTP 200
        """
        self.conn.request("GET", "/work/5416.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_journal_json(self):
        """
        Journal JSON
        Verify that /journal.json returns HTTP 200
        """
        self.conn.request("GET", "/journal.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_taxonomy_json(self):
        """
        Taxonomy JSON
        Verify that /taxonomy.json returns HTTP 200
        """
        self.conn.request("GET", "/taxonomy.json")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

    def test_search_box(self):
        """
        Search Box
        Verify autocomplete works. Easy test: "time" at /entity.json?q=time
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
        Verify log-generating script works at /owl
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
        Verify user is able to Enable evaluations, choose an item, choose a setting, and submit an evaluation to /idea/1488
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
        Verify evaluation submissions append to database at /idea/1488
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
        Verify items are not already in database. Check sep_dir fields at /admin
        """
        new = sep.new_entries()
        entries_in_db = 0
        for entry in new:
            if(len(Session.query(Entity).filter(Entity.sep_dir == entry).all()) > 0):
                entries_in_db += 1
                print entry
        self.assertEqual(entries_in_db, 0)

    def test_entity_creation(self):
        """
        Entity Creation
        Verify a new entity can be created. Check /entity/new
        """
        self.conn.request("POST", "/idea?_method=POST&label=test")
        result = self.conn.getresponse()
        self.assertLessEqual(result.status, 400)

#### NEED TO ACCESS THE NUMBER IN THE URL FOR THE 'Test' entity in order to delete it
   # def test_entity_delete(self):
   #     self.conn.request("POST", "/idea?_method=POST&label=test")
   #     result = self.conn.getresponse()
   #     self.assertLessEqual(result.status, 400)
   #     result.

if __name__ == '__main__':
   unittest2.main()
