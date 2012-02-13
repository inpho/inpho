import logging
import re

from inpho.model import Session, Idea

class Lexicon(object):
    """
    Abstract class for all Lexicon objects.
    """
    def __init__(self, terms=None):
        """
        Dummy constructor. Not sure if best practices dictate that I should
        raise NotImplementedError or not for an abstract class.
        """
        if terms is None:
            self.terms = []
        else:
            self.terms = terms

    def sublexicon(self, string):
        """
        Returns a new Lexicon consisting of the subset of terms which occur in
        the document contained in the given string. This is designed to reduce
        computational complexity when loooking at subsets of a document. For
        example, when processing sentences, one could use the
        self.sublexicon(reader.document) to reduce the amount of looping done on
        each individual sentence.
        """
        return Lexicon(self.occurrences(string))

    def occurrences(self, string):
        """
        Returns a list of terms which occur in the document contained in the
        given string.    
        Semantically equivalent to 
        [term for term in self.terms if term in string]
        """
        # construct a list of all terms which appear
        occurrences = []

        # iterate over all terms and search patterns
        for term in self.terms:
            for pattern in term.searchpatterns:
                # error handling for faulty patterns. Perhaps this should be
                # moved to processing on the inpho.corpus.lexicon.Term objects?
                try:
                    if re.search(pattern, string, flags=re.IGNORECASE):
                        # add to the list of occurrences, proceed to next term
                        occurrences.append(term)
                        break    # move to next term, rather than next pattern
                except re.error:
                    logging.warning('Term %d (%s) pattern "%s" failed' % 
                                    (term.ID, term.label, pattern))
                    term.searchpatterns.remove(pattern)

        return occurrences

    def document_occurrences(self, reader):
        """
        Returns a list of terms which occur in the document contained in the
        given inpho.corpus.Reader object.
    
        Semantically equivalent to 
        [term for term in self.terms if term in reader.document]
        """
        return self.occurrences(reader.document)


    def sentence_occurrences(self, reader, remove_overlap=False):
        """
        Returns a list of lists representing the terms occuring in each sentence.
        Semantically equivalent to: 
        [[term for term in terms if term in sent] for sent in document]
        """
        # Create a list of lists containing the collection of terms which cooccurr
        # in a sentence
        doc_lexicon = self.sublexicon(reader.occurrences)
        occurrences = [doc_lexicon.occurrences(sentence)
                           for sentence in reader.sentences]
        
        # remove overlapping elements - "The David Problem"
        if remove_overlap:
            occurrences = [Lexicon._remove_overlap(sentence) 
                               for sentence in occurrences]

        # remove empty elements
        occurrences = [sentence for sentence in occurrences if sentence]

        return occurrences

    @staticmethod
    def _remove_overlap(occurrences):
        """
        Takes a list of Term occurrences, and removes those which have
        overlapping labels. Designed to solve "The David Problem".
        """
        to_remove = set()
              
        # build set of terms to remove
        for inside in occurrences:
            for term in occurrences:
                if term != inside and\
                   inside.label.find(term.label) != -1:
                   to_remove.add(term)

        # filter out terms to remove
        return [term for term in occurrences if term not in to_remove]


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
        # select all terms from the database and delink them
        self.terms = Session.query(Idea).all()
        Session.expunge_all()
        Session.close()
        
        # fix search patterns to find word breaks, rather than just spaces
        for term in terms:
            newpatterns = []
            for pattern in term.searchpatterns:
                if '(' in pattern and ')' in pattern:
                    pattern = pattern.replace('( ', '(\\b')
                    pattern = pattern.replace(' )', '\\b)')
                else:
                    pattern = '\\b%s\\b' % pattern.strip()
    
                newpatterns.append(pattern)
    
            term.searchpatterns = newpatterns

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

