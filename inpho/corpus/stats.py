#loadCorpus

# Iterate through corpus dir and find all sep_dirs and index files
# Alternatively, iterate through sep_dirs of SQL

# Open HTML file and grab sentence list
# 
# title.replaceAll(" \\(stanford encyclopedia of philosophy\\)", "");                 
# title.replaceAll("sep: ", "");   

# documentString which is just sentenceList.join()

# appearList is set of all terms which appear in the sentence
# occurList is set of all terms occuring in the document

import logging
import re
import subprocess
from collections import defaultdict

# http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tokenize.punkt.PunktSentenceTokenizer-class.html
from nltk.tokenize import PunktSentenceTokenizer as Tokenizer

def get_document_occurrences(document, terms, doc_terms=None):
    """
    Returns a list of terms occuring in the document. 
    Semantically equivalent to [term for term in terms if term in document]

    Primarily used by :func:`get_sentence_occurrences()`.
    """

    occurrences = []
    
    # iterate over terms to be scanned
    for term in terms:
        if term not in doc_terms:
            # build list of search patterns starting with label
            pattern = ['\b%s\b' % term.label]
            pattern.extend(term.searchpatterns)
            for pattern in term.searchpatterns:
                try:
                    if re.search(pattern, document, flags=re.IGNORECASE):
                        occurrences.append(term)
                        break
                except re.error:
                    logging.warning('Term %d (%s) pattern "%s" failed' % 
                                    (term.ID, term.label, pattern))
                    term.searchpatterns.remove(pattern)

    if doc_terms:
        occurrences.extend(doc_terms)

    return occurrences

def get_sentence_occurrences(document, terms, doc_terms=None, terms_present=None, 
                             remove_overlap=False, remove_duplicates=False,
                             remove_duplicate_doc_terms=True):
    """
    Returns a list of lists representing the terms occuring in each sentence.
    Semantically equivalent to: 
    [[term for term in terms if term in sent] for sent in document]

    Order of optional operations is: remove duplicates, remove overlap, 
    add doc terms, remove duplicate doc terms
    """
    # get list of terms in the document to narrow sentence-level search
    if terms_present is None:
        terms_present = set(get_document_occurrences(document, terms, doc_terms))

    # Use a Tokenizer from NLTK to build a sentence list
    tokenizer = Tokenizer(document)
    sentences = tokenizer.tokenize(document)
    
    # Create a list of lists containing the collection of terms which cooccurr
    # in a sentence
    occurrences = []
    for sentence in sentences:
        sentence_occurrences = [] 

        for term in terms_present:
            if term not in doc_terms:
                # build list of search patterns starting with label
                pattern = ['\b%s\b' % term.label]
                pattern.extend(term.searchpatterns)

                for pattern in term.searchpatterns:
                    try:
                        # search for any occurrence of term, stop when found
                        if re.search(pattern, document, flags=re.IGNORECASE):
                            sentence_occurrences.append(term)
                            break
                    except re.error:
                        logging.warning('Term %d (%s) pattern "%s" failed' % 
                                        (term.ID, term.label, pattern))
                        term.searchpatterns.remove(pattern)

        # remove duplicates
        if remove_duplicates:
            sentence_occurrences = list(set(sentence_occurrences))

        # remove overlapping elements
        if remove_overlap:
            to_remove = set()
            
            # build set of terms to remove
            for inside in sentence_occurrences:
                for term in sentence_occurrences:
                    if term != inside and\
                        inside.label.find(term.label) != -1:
                        to_remove.add(term)

            # remove terms
            for term in to_remove:
                sentence_occurrences.remove(term)

        # add to list of sentences if any terms are found
        if sentence_occurrences:
            # append global terms
            if doc_terms and remove_duplicate_doc_terms:
                doc_terms = [term for term in doc_terms 
                                 if term not in sentence_occurrences]
                sentence_occurrences.extend(doc_terms)
            elif doc_terms:
                sentence_occurrences.extend(doc_terms)

            occurrences.append(sentence_occurrences)
    
    return occurrences

def prepare_apriori_input(document, terms, doc_terms=None, add_newline=True,
                          remove_overlap=False, document_sentence=False): 
    '''
    Prepares "shopping basket" input for the apriori miner, where each sentence
    stands on its own line.
    '''

    # grab document-level occurrences, reused in sentence occurrences and
    # summary sentence
    occurrences = set(get_document_occurrences(document, terms, doc_terms))

    # grab sentence occurrences
    sentence_occurrences = get_sentence_occurrences(
        document, terms, doc_terms, terms_present=occurrences,
        remove_overlap=remove_overlap, remove_duplicates=True, 
        remove_duplicate_doc_terms=True)

    lines = []

    # add summary sentence (optional)
    if document_sentence:
        lines.append(' '.join([str(term.ID) for term in occurrences]))

    # add each sentence
    for sent_occur in sentence_occurrences:
        lines.append(' '.join([str(term.ID) for term in sent_occur]))

    # add newlines (for file printing)
    if add_newline:
        lines = [line + '\n' for line in lines]

    return lines

def prepare_apriori_input_from_file(occurrence_filename, terms, 
                                    add_newline=True):
    '''
    Prepares "shopping basket" input for the apriori miner from a file of
    sentence-lvel occurrences.
    '''
    # build up terms, as they will occur in the file
    terms = [str(term.ID) for term in terms]

    with open(occurrence_filename) as f:
        lines = []
        for line in f:
            line = [term for term in line.split() if term in terms]
            lines.append(' '.join(line))
    
    # add newlines (for file printing)
    if add_newline:
        lines = [line + '\n' for line in lines]

    return lines

def apriori(input_filename='output.txt', output_filename='edges.txt'):
    args = ['apriori', input_filename, output_filename,
            '0.00000000000000001', '0.00000000000000001']
    return subprocess.call(args)


def process_edges(occurrences_filename='output.txt', edges_filename='edges.txt'):
    # process occurrence and cooccurrence data
    occurrences = defaultdict(lambda: defaultdict(int))
    with open(occurrences_filename) as f:
        for line in f:
            ids = line.split()

            for ante in ids:
                for cons in ids:
                    occurrences[ante][cons] += 1

    edges = defaultdict(dict)
    with open(edges_filename) as f:
        for line in f:
            ante,cons,confidence,jweight = line.split()
            edges[(ante,cons)] = {'confidence':float(confidence), 
                                  'jweight':float(jweight),
                                  'occurrences':occurrences[ante][cons]}
    return edges

from math import log
def calculate_node_entropy(edges):
    probabilities = defaultdict(lambda: defaultdict(float))
    for edge,properties in edges.iteritems():
        ante,cons = edge
        probabilities[ante][cons] = properties['confidence']
    
    ents = defaultdict(float)
    for ante,conses in probabilities.iteritems():
        total_prob = sum(conses.values())
        normalized_probs = [x / total_prob for x in conses.values()]

        Hx = sum([x * (log(x) / log(2)) for x in normalized_probs])

        ents[ante] = -Hx

    return ents

def calculate_edge_weight(edges, ents):
    weights = defaultdict(float)
    if ents:
        max_entropy = max(ents.values())
        for edge, properties in edges.iteritems():
            ante,cons = edge
            entropy_diff = ents[ante] - ents[cons]
            entropy_norm = entropy_diff / max_entropy
            properties['weight'] = properties['jweight'] * entropy_norm
    else:
        print "ERROR PROCESSING EDGES. NO ENTROPY VALUES."

    return edges    
