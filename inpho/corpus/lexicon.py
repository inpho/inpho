from inpho.model import Session, Idea

class Lexicon(object):
    """
    Abstract class for all Lexicon objects.
    """
    @property
    def terms(self):
        raise NotImplementedError

class CorpusLexicon(object):
    """
    CorpusLexicon is a default reader that takes a collection of readers and
    finds all terms within that corpus and instantiates them within Term
    objects.
    """
    def __init__(self, readers):
        terms = set()
        for document in readers:
            terms.add(document.words)
        self.terms = [Term(i, term) for i, term in enumerate(terms)]

class DatabaseLexicon(object):
    """
    DatabaseLexicon imports term lists from inpho.model.
    """
    def __init__(self, entity_type=Idea):
        self.terms = Session.query(Idea).all()

class Term(object):
    """
    Basic Term object. The Entity objects in the InPhO database also correspond
    to this interface.
    """
    def __init__(self, ID, label, search_patterns=None):
        self.ID = ID
        self.label = label
        self.search_patterns = [self.label]
        if search_patterns is not None:
            self.search_patterns.extend(search_patterns)

