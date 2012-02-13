import logging
import re

from inpho.model import Session, Idea

class Lexicon(object):
    """
    Abstract class for all Lexicon objects.
    """
    def __init__(self):
        """
        Dummy constructor. Not sure if best practices dictate that I should
        raise NotImplementedError or not for an abstract class.
        """
        self.terms = []

    def occurrences(self, reader):
        """
        Returns a list of terms which occur in the document contained in the
        given inpho.corpus.Reader object.
        """
        # construct a list of all terms which appear
        occurrences = []

        # iterate over all terms and search patterns
        for term in self.terms:
            for pattern in term.searchpatterns:
                # error handling for faulty patterns. Perhaps this should be
                # moved to processing on the inpho.corpus.lexicon.Term objects?
                try:
                    if re.search(pattern, reader.document, flags=re.IGNORECASE):
                        # add to the list of occurrences, proceed to next term
                        occurrences.append(term)
                        break    # move to next term, rather than next pattern
                except re.error:
                    logging.warning('Term %d (%s) pattern "%s" failed' % 
                                    (term.ID, term.label, pattern))
                    term.searchpatterns.remove(pattern)

        return occurrences

class CorpusLexicon(Lexicon):
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

class DatabaseLexicon(Lexicon):
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
    def __init__(self, ID, label, searchpatterns=None):
        self.ID = ID
        self.label = label
        self.searchpatterns = ['\b%s\b' % self.label]
        if searchpatterns is not None:
            self.searchpatterns.extend(searchpatterns)

