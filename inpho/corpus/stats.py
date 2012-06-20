"""
Module containing statistical methods for the InPhO data mining process.
"""

import logging
import re
import subprocess
from collections import defaultdict

# http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tokenize.punkt.PunktSentenceTokenizer-class.html
from nltk.tokenize import PunktSentenceTokenizer as Tokenizer

from inpho import config

def get_document_occurrences(document, terms):
    """
    Returns a list of terms occuring in the document. 
    Semantically equivalent to [term for term in terms if term in document]

    Primarily used by :func:`get_sentence_occurrences()`.
    """

    occurrences = []
    
    # iterate over terms to be scanned
    for term in terms:
        # build list of search patterns starting with label
        patterns = term.searchpatterns
        for pattern in patterns:
            try:
                if re.search(pattern, document, flags=re.IGNORECASE):
                    occurrences.append(term)
                    break
            except re.error:
                logging.warning('Term %d (%s) pattern "%s" failed' % 
                                (term.ID, term.label, pattern))
                term.searchpatterns.remove(pattern)

    return occurrences

def get_sentence_occurrences(document, terms, terms_present=None, 
                             remove_overlap=False, remove_duplicates=False):
    """
    Returns a list of lists representing the terms occuring in each sentence.
    Semantically equivalent to: 
    [[term for term in terms if term in sent] for sent in document]

    Order of optional operations is: remove duplicates, remove overlap, 
    add doc terms, remove duplicate doc terms
    """
    # get list of terms in the document to narrow sentence-level search
    if terms_present is None:
        terms_present = set(get_document_occurrences(document, terms))

    # Use a Tokenizer from NLTK to build a sentence list
    tokenizer = Tokenizer(document)
    sentences = tokenizer.tokenize(document)
    logging.info("scanning %d sentences for %d terms" % (len(sentences), len(terms)))
    
    # Create a list of lists containing the collection of terms which cooccurr
    # in a sentence
    occurrences = []
    for sentence in sentences:
        sentence_occurrences = [] 

        for term in terms_present:
            # build list of search patterns starting with label
            patterns = term.searchpatterns

            for pattern in patterns:
                try:
                    # search for any occurrence of term, stop when found
                    if re.search(pattern, sentence, flags=re.IGNORECASE):
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
            occurrences.append(sentence_occurrences)
    
    return occurrences

def occurrences(document, terms, title=None, remove_overlap=False,
                format_for_file=False, output_filename=None):
    # grab document-level occurrences, reused in sentence occurrences and
    # summary sentence
    occurrences = set(get_document_occurrences(document, terms))

    # grab sentence occurrences
    sentence_occurrences = get_sentence_occurrences(
        document, terms, terms_present=occurrences,
        remove_overlap=remove_overlap, remove_duplicates=True)


    if not format_for_file:
        # return raw occurrences
        return sentence_occurrences

    else:
        # format for file writing
        lines = []
        for sent_occur in sentence_occurrences:
            line = ' '.join([str(term.ID) for term in sent_occur])
            line = line + '\n'
            if title:
                line = title + ' ' + line
            
            lines.append(line)

        if output_filename:
            with open(output_filename, 'w') as f:
                f.writelines(lines)

        return lines

def prepare_apriori_input(occurrence_filename, terms, doc_terms=None):
    '''
    Prepares "shopping basket" input for the apriori miner from a file of
    sentence-lvel occurrences.
    '''
    # build up terms, as they will occur in the file
    terms = [str(term.ID) for term in terms]
    summary = defaultdict(set)

    with open(occurrence_filename) as f:
        lines = []
        for line in f:
            lterms = line.split()
            first = lterms[0]       # Save for doc_terms processing

            line = [term for term in lterms if term in terms]

            # append doc_terms
            if line and doc_terms is not None:
                # search for doc terms, remove duplicates, add to line
                key_terms = [str(term.ID) for term in doc_terms[first]]
                key_terms = [term for term in key_terms 
                                 if term not in lterms and term in terms]
                if key_terms:
                    line.extend(key_terms)
            
            summary[first].update(line)

            # do not add blank or singleton lines
            if len(line) > 1:
                line.append('\n')
                lines.append(' '.join(line))

    for line in summary.itervalues():
        line = list(line)
        line.append('\n')
        lines.append(' '.join(line))
    
    return lines

def apriori(input_filename='output.txt', output_filename='edges.txt'):
    apriori_bin = config.get('corpus', 'apriori_bin')
    args = [apriori_bin, input_filename, output_filename,
            '0.00000000000000001', '0.00000000000000001']
    return subprocess.call(args)


def process_edges(graph_filename='output.txt', edges_filename='edges.txt',
                  occur_filename='occurrences.txt', doc_terms=None):
    # process occurrence and cooccurrence data
    graph = defaultdict(lambda: defaultdict(int))
    with open(graph_filename) as f:
        for line in f:
            ids = line.split()

            for ante in ids:
                for cons in ids:
                    graph[ante][cons] += 1
    
    occurrences = occurs_in(occur_filename, doc_terms)

    edges = defaultdict(dict)
    with open(edges_filename) as f:
        for line in f:
            ante,cons,confidence,jweight = line.split()
            edges[(ante,cons)] = {'confidence':float(confidence), 
                                  'jweight':float(jweight),
                                  'occurs_in':occurrences[ante][cons],
                                  'graph':graph[ante][cons]}
    return edges

def occurs_in(occur_filename='occurrences.txt', doc_terms=None):
    occurrences = defaultdict(lambda: defaultdict(int))
    with open(occur_filename) as f:
        for line in f:
            lterms = line.split()
            article = lterms[0]

            if doc_terms:
                for term in lterms[1:]:
                    for doc in doc_terms[article]:
                        occurrences[str(doc.ID)][term] += 1
            else:
                for term in lterms[1:]:
                    occurrences[article][term] += 1

    return occurrences

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
