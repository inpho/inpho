import os
import os.path
from BeautifulSoup import BeautifulSoup
from sqlalchemy.orm import subqueryload
from sqlalchemy import and_, or_, not_

import inpho.corpus.stats as dm
from inpho.model import Idea, Thinker, Entity, Session 

def extract_article_body(filename):
    f=open(filename)
    doc=f.read()
    soup=BeautifulSoup(doc)

    # rip out bibliography
    biblio_root = soup.findAll('h2', text='Bibliography')
    if biblio_root:
        biblio_root = biblio_root[-1].findParent('h2')
        biblio = [biblio_root]
        biblio.extend(biblio_root.findNextSiblings())
        biblio = [elm.extract() for elm in biblio]

    # grab modified body 
    body=soup.find("div", id="aueditable")

    return body.text

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

    filename = article.get_filename(corpus_root)
    if filename and os.path.isfile(filename):
        print "processing:", article.sep_dir, filename
        try: 
            doc = extract_article_body(filename)
            lines = dm.prepare_apriori_input(doc, terms, article)
        except:
            print "ERROR PROCESSING:", article.sep_dir, filename
    else:
        print "BAD SEP_DIR:", article.sep_dir

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
    
    articles = Session.query(entity_type).filter(entity_type.sep_dir!='').all()
   
    # parallel processing of articles
    p = Pool()
    args = [(title, terms, entity_type, None, corpus_root) for title in articles]
    doc_lines = p.map(process_wrapper, args)
    p.close()

    # write graph output to file
    with open(output_filename, 'w') as f:
        for lines in doc_lines:
            f.writelines(lines)

import subprocess

def complete_mining(entity_type=Idea, filename='graph.txt', root='./',
                    corpus_root='corpus/'):
    occur_filename = os.path.abspath(root + "graph-" + filename)
    edge_filename = os.path.abspath(root + "edge-" + filename)
    sql_filename = os.path.abspath(root + "sql-" + filename)


    print "processing articles..."
    process_articles(entity_type, occur_filename, corpus_root=corpus_root)

    print "running apriori miner..."
    dm.apriori(occur_filename, edge_filename)
    
    print "processing edges..."
    edges = dm.process_edges(occur_filename, edge_filename)
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

    for term_id, entropy in ents.iteritems():
        term = Session.query(Idea).get(term_id)
        if term:
            term.entropy = entropy

    Session.flush()
    Session.commit()


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
    
    LOAD DATA INFILE '%(filename)s'
    INTO TABLE %(table)s
    FIELDS TERMINATED BY '::'
    (ante_id, cons_id, confidence, jweight, weight);
    
    """ % {'filename' : sql_filename, 'table' : table })


if __name__ == "__main__":
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read('sql.ini')
    corpus_root = config.get('corpus', 'path') 

    from optparse import OptionParser

    usage = "usage: %prog [options] config_file"
    parser = OptionParser(usage)
    parser.set_defaults(mode='all')
    parser.add_option("-a", "--all", action="store_const",
                      dest='mode', const='all',
                      help="mine all edges [default]")
    parser.add_option("-i", "--idea", action="store_const",
                      dest='mode', const='idea',
                      help="mine only idea-idea edges")
    parser.add_option("-t", "--thinker", action="store_const",
                      dest='mode', const='thinker',
                      help="mine only thinker-thinker edges")
    options, args = parser.parse_args()

    if options.mode == 'all':
        complete_mining(Entity, filename="all", corpus_root=corpus_root)

    elif options.mode == 'idea':
        complete_mining(Idea, filename="idea", corpus_root=corpus_root)

    elif options.mode == 'thinker':
        complete_mining(Thinker, filename="thinker", corpus_root=corpus_root)

