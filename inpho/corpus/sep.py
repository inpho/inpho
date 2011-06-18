import logging
import os.path
import re

from BeautifulSoup import BeautifulSoup
from sqlalchemy.orm import subqueryload
from sqlalchemy import and_, or_, not_

import inpho.corpus.stats as dm
from inpho.model import Idea, Thinker, Entity, Session 

def extract_article_body(filename):
    f = open(filename)
    doc = f.read()
    soup = BeautifulSoup(doc, convertEntities=["xml", "html"])

    # rip out bibliography
    biblio_root = soup.findAll('h2', text='Bibliography')
    if biblio_root:
        biblio_root = biblio_root[-1].findParent('h2')
        biblio = [biblio_root]
        biblio.extend(biblio_root.findNextSiblings())
        biblio = [elm.extract() for elm in biblio]

    # grab modified body 
    body = soup.find("div", id="aueditable")
    if body is not None:
        # remove HTML escaped characters
        body = re.sub("&\w+;", "", body.text)
    
        return body
    else:
        logging.error('Could not extract text from %s' % filename)

        return ''

def select_terms(entity_type=Idea):
    # process entities
    ideas = Session.query(entity_type)
    ideas = ideas.options(subqueryload('_spatterns'))
    # do not process Nodes or Journals
    ideas = ideas.filter(and_(Entity.typeID!=2, Entity.typeID!=4))
    return ideas.all()
     

def process_article(article, terms=None, entity_type=Idea, output_filename=None,
                    corpus_root='corpus/'):
    if terms is None:
        terms = select_terms(entity_type)
    

    lines = []

    filename = os.path.join(corpus_root, article, 'index.html')
    article_terms = Session.query(entity_type)
    article_terms = article_terms.filter(entity_type.sep_dir==article)
    article_terms = article_terms.all()
    if filename and os.path.isfile(filename):
        print "processing:", article, filename
        doc = extract_article_body(filename)
        lines = dm.prepare_apriori_input(doc, terms, article_terms)
    else:
        logging.warning("BAD SEP_DIR: %s" % article)

    if output_filename:
        with open(output_filename, 'w') as f:
            f.writelines(lines)
    else:
        return lines

from multiprocessing import Pool

def process_wrapper(args):
    return process_article(*args)

def process_articles(entity_type=Entity, output_filename='output-all.txt',
                     corpus_root='corpus/'):
    terms = select_terms(entity_type)
    Session.expunge_all()
    Session.close()
    
    articles = Session.query(Entity.sep_dir).filter(Entity.sep_dir!=None)
    articles = articles.filter(Entity.sep_dir!='')
    articles = articles.distinct().all()
    articles = [a[0] for a in articles]
   
    # parallel processing of articles
    p = Pool()
    args = [(title, terms, entity_type, None, corpus_root) for title in articles]
    doc_lines = p.map(process_wrapper, args)
    p.close()

    #serial processing for tests
    '''
    doc_lines = []
    for title in articles:
        lines = process_article(title, terms, entity_type, None, corpus_root)
        doc_lines.append(lines)
    '''

    # write graph output to file
    print output_filename
    with open(output_filename, 'w') as f:
        for lines in doc_lines:
            f.writelines(lines)

def filter_apriori_input(occur_filename, output_filename, entity_type=Idea):
    #select terms
    terms = select_terms(entity_type)
    Session.expunge_all()
    Session.close()

    lines = dm.prepare_apriori_input_from_file(occur_filename, terms)
    
    with open(output_filename, 'w') as f:
        f.writelines(lines)



import subprocess
def complete_mining(entity_type=Idea, filename='graph.txt', root='./',
                    corpus_root='corpus/', update_entropy=False,
                    update_occurrences=False): 
    occur_filename = os.path.abspath(root + "occurrences.txt")
    graph_filename = os.path.abspath(root + "graph-" + filename)
    edge_filename = os.path.abspath(root + "edge-" + filename)
    sql_filename = os.path.abspath(root + "sql-" + filename)

    if update_occurrences:
        print "processing articles..."
        process_articles(entity_type, occur_filename, corpus_root=corpus_root)

    print "filtering occurrences..."
    filter_apriori_input(occur_filename, graph_filename, entity_type)

    print "running apriori miner..."
    dm.apriori(graph_filename, edge_filename)
    
    print "processing edges..."
    edges = dm.process_edges(graph_filename, edge_filename)
    ents = dm.calculate_node_entropy(edges)
    edges = dm.calculate_edge_weight(edges, ents)
    
    print "creating sql files..."

    with open(sql_filename, 'w') as f:
        for edge, props in edges.iteritems():
            ante,cons = edge
            row = "%s::%s" % edge
            row += "::%(confidence)s::%(jweight)s::%(weight)s\n" % props
            f.write(row)

    print "updating term entropy..."

    if update_entropy:
        for term_id, entropy in ents.iteritems():
            term = Session.query(Idea).get(term_id)
            if term:
                term.entropy = entropy

        Session.flush()
        Session.commit()
        Session.close()

    update_graph(entity_type, sql_filename)

def update_graph(entity_type, sql_filename):
    # Import SQL statements
    if entity_type == Idea:
        table = "idea_graph_edges"
    elif entity_type == Thinker:
        table = "thinker_graph_edges"
    else:
        table = "idea_thinker_graph_edges"

    connection = Session.connection()

    print "deleting old graph information ..."
    connection.execute("""
    DELETE FROM %(table)s;
    """ % {'filename' : sql_filename, 'table' : table })
    
    print "inserting new graph information"
    connection.execute("""
    SET foreign_key_checks=0;
    LOAD DATA INFILE '%(filename)s'
    INTO TABLE %(table)s
    FIELDS TERMINATED BY '::'
    (ante_id, cons_id, confidence, jweight, weight);
    SET foreign_key_checks=1;
    """ % {'filename' : sql_filename, 'table' : table })
    Session.close()


if __name__ == "__main__":
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read('sql.ini')
    corpus_root = config.get('corpus', 'path') 

    from optparse import OptionParser

    usage = "usage: %prog [options] config_file"
    parser = OptionParser(usage)
    parser.set_defaults(type='all', mode='complete', update_entropy=False,
                        update_occurrences=False)
    parser.add_option("-a", "--all", action="store_const",
                      dest='type', const='all',
                      help="mine all edges [default]")
    parser.add_option("-i", "--idea", action="store_const",
                      dest='type', const='idea',
                      help="mine only idea-idea edges")
    parser.add_option("-t", "--thinker", action="store_const",
                      dest='type', const='thinker',
                      help="mine only thinker-thinker edges")
    parser.add_option("--complete", action="store_const",
                      dest='mode', const='complete',
                      help="complete data mining process [default]")
    parser.add_option("--entropy", action="store_true",
                      dest='update_entropy',
                      help="data mining, with entropy updates")
    parser.add_option("--occur", action="store_true",
                      dest='update_occurrences',
                      help="data mining, with occurrence file generation")
    parser.add_option("--load", action="store_const",
                      dest='mode', const='load',
                      help="load data from sql files")
    options, args = parser.parse_args()

    filename_root = options.type


    entity_type = Entity
    if options.type == 'idea':
        entity_type = Idea
    elif options.type == 'thinker':
        entity_type = Thinker
    
    if options.mode == 'complete':
        complete_mining(entity_type, 
                        filename=filename_root, 
                        corpus_root=corpus_root, 
                        update_entropy=options.update_entropy,
                        update_occurrences=options.update_occurrences)
    elif options.mode == 'load':
        sql_filename = os.path.abspath(corpus_root + "sql-" + filename_root)
        update_graph(entity_type, sql_filename)
