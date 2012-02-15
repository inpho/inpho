"""
Module containing statistical methods for the InPhO data mining process.
"""

import logging
import re
import subprocess
from collections import defaultdict

from inpho import config

def prepare_occurrences_file(reader, lexicon, title=None, 
                             remove_overlap=False):
    """
    Prepares the lines ontaining the sentence occurrence data for the given
    reader and lexicon. Optional argument for writing the article title as an
    option for multi-corpus files. Returns the list of lines written.
    """
    sentence_occurrences = lexicon.sentence_occurrences(
        reader, remove_overlap=remove_overlap)

    lines = []

    # prebuffer lines in memory
    for sentence in sentence_occurrences:
        line = ' '.join([str(term.ID) for term in sentence])
        line += '\n'

        # append article title, if provided
        if title:
            line = title + ' ' + line
        
        lines.append(line)

    return lines


def write_occurrences_file(reader, lexicon, filename, title=None, append=False,
                           remove_overlap=False):
    """
    Write an file containing the sentence occurrence data for the given reader
    and lexicon. Optional argument for writing the article title as an option
    for multi-corpus files. Returns the list of lines written.
    """
    lines = prepare_occurrences_file(reader, lexicon, title, remove_overlap)

    # write file to disk
    mode = 'a' if append else 'w'
    with open(filename, mode) as f:
        f.writelines(lines)

    return lines

def prepare_apriori_input(occurrence_filename, lexicon, doc_terms=None):
    '''
    Prepares "shopping basket" input for the apriori miner from a file of
    sentence-lvel occurrences.
    '''
    # build up terms, as they will occur in the file
    terms = [str(term.ID) for term in lexicon.terms]
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

def write_apriori_input(filename):
    pass

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

if __name__ == '__main__':
    """ Quick test cases """
    from inpho.corpus.reader import SEPReader
    from inpho.corpus.lexicon import DatabaseLexicon

    reader = SEPReader('epistemology')
    lexicon = DatabaseLexicon()

    print prepare_occurrences_file(reader, lexicon)
