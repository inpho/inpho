from collections import defaultdict
import csv
import logging
from multiprocessing import Pool
import os.path
import re
import subprocess

from BeautifulSoup import BeautifulSoup
from sqlalchemy.orm import subqueryload
from sqlalchemy import and_, or_, not_

from inpho import config
from inpho.corpus.fuzzymatch import fuzzymatch_all as fuzzymatch
import inpho.corpus.stats as dm
from inpho.model import Idea, Thinker, Entity, Session 

def extract_article_body(filename):
    """
    Extracts the article body from the SEP article at the given filename. Some
    error handling is done to guarantee that this function returns at least the
    empty string. Check the error log.
    """
    f = open(filename)
    doc = f.read()
    soup = BeautifulSoup(doc, convertEntities=["xml", "html"])

    # rip out bibliography
    biblio_root = soup.findAll('h2', text='Bibliography')
    if biblio_root:
        biblio_root = biblio_root[-1].findParent('h2')
        if biblio_root:
            biblio = [biblio_root]
            biblio.extend(biblio_root.findNextSiblings())
            biblio = [elm.extract() for elm in biblio]
        else:
            logging.error('Could not extract bibliography from %s' % filename)

    # grab modified body 
    body = soup.find("div", id="aueditable")
    if body is not None:
        # remove HTML escaped characters
        body = re.sub("&\w+;", "", body.text)
    
        return body
    else:
        logging.error('Could not extract text from %s' % filename)

        return ''

def article_path(sep_dir):
    if published(sep_dir):
        corpus_root = config.get('corpus', 'path')
        path = os.path.join(corpus_root, sep_dir, 'index.html')
    elif copy_edit(sep_dir):
        corpus_root = config.get('corpus', 'edit_path')
        path = os.path.join(corpus_root, sep_dir, 'index.html')
        logging.info('Processing unpublished article ' + sep_dir)
    else:
        path = ''

    return path

def published(sep_dir, log_root=None):
    """
    Checks if the given article is published.
    """
    return get_status_code(sep_dir, 'eP', log_root);


def copy_edit(sep_dir, log_root=None):
    """
    Checks if the given article is in copy edit mode.
    """
    return get_status_code(sep_dir, 'eq', log_root);

def get_status_code(sep_dir, code, log_root=None):
    """
    Checks if the given article has the given status code.
    """
    if log_root is None:
        log_root = config.get('corpus', 'log_path')

    log_path = os.path.join(log_root, sep_dir)
    if os.path.exists(log_path):
        with open(log_path) as log:
            for line in log:
                #use the published flag 
                if ('::' + code) in line:
                    return True

    return False

def get_titles():
    """
    Returns a dictionary of { sep_dir : title } pairs.
    """
    entries = os.path.join(config.get('corpus', 'db_path'), 'entries.txt')
    
    titles = {}
    with open(entries) as f:
        for line in f:
            sep_dir, title, rest = line.split('::', 2)
            title = title.replace(r"\'", "'")
            titles[sep_dir] = title

    return titles

def get_categories():
    """
    Returns a dictionary of { sep_dir : title } pairs.
    """
    entries = os.path.join(config.get('corpus', 'db_path'), 'entries.txt')
    
    categories = {}
    with open(entries) as f:
        for line in f:
            sep_dir, rest = line.split('::', 1)
            category = line.split('::')[-3]
            category = category.replace(r"\'", "'")
            categories[sep_dir] = category

    return categories 

def get_title(sep_dir):
    """
    Returns the title for the given sep_dir
    """
    entries = os.path.join(config.get('corpus', 'db_path'), 'entries.txt')
    
    with open(entries) as f:
        for line in f:
            dir, title, rest = line.split('::', 2)
            if dir == sep_dir:
                return title.replace(r"\'", "'")

    raise KeyError("Invalid sep_dir")

def new_entries():
    """
    Returns a list of all entries which do not have a corresponding InPhO Entity.
    """

    # get list of all entries in database
    sep_dirs = Session.query(Entity.sep_dir).filter(Entity.sep_dir!='').all()
    sep_dirs = [row[0] for row in sep_dirs]

    # get list of all entries in the SEP database
    entries = os.path.join(config.get('corpus', 'db_path'), 'entries.txt')

    # build list of new entries
    new_sep_dirs = []
    with open(entries) as f:
        for line in f:
            sep_dir = line.split('::', 1)[0]
            try:
                if sep_dir not in sep_dirs and copy_edit(sep_dir):
                    # published entry not in database, add to list of entries
                    new_sep_dirs.append(sep_dir)
            except IOError:
                # skip IOErrors, as these indicate potential entries w/o logs
                continue

    # remove the sample entry
    try:
        new_sep_dirs.remove('sample')
    except ValueError:
        pass

    return new_sep_dirs

def fuzzymatch_new():
    """
    Writes the fuzzymatch data to the cache specified in the config file.
    """
    fuzzy_path = config.get('corpus', 'fuzzy_path')
    titles = get_titles()
    for entry in new_entries():
        print entry
        matches = fuzzymatch(titles[entry])
        with open(os.path.join(fuzzy_path, entry), 'wb') as f:
            writer = csv.writer(f)
            for match, prob in matches:
                writer.writerow([match.ID, match.label, prob])
        

def select_terms(entity_type=Idea):
    """
    Returns a list of all terms of a given entity type.
    """

    # process entities
    ideas = Session.query(entity_type)
    ideas = ideas.options(subqueryload('_spatterns'))
    # do not process Nodes or Journals
    ideas = ideas.filter(and_(Entity.typeID!=2, Entity.typeID!=4))
    return ideas.all()
     

def process_article(article, terms=None, entity_type=Idea, output_filename=None,
                    corpus_root='corpus/'):
    """
    Processes a single article for apriori input.
    """
    if terms is None:
        terms = select_terms(entity_type)
    

    lines = []

    filename = article_path(article)
    article_terms = Session.query(entity_type)
    article_terms = article_terms.filter(entity_type.sep_dir==article)
    article_terms = article_terms.all()
    if filename and os.path.isfile(filename):
        logging.info("processing: %s %s" % (article, filename))
        doc = extract_article_body(filename)
        lines = dm.occurrences(doc, terms, title=article,
                               remove_overlap=False,
                               format_for_file=True,
                               output_filename=output_filename)
    else:
        logging.warning("BAD SEP_DIR: %s" % article)

    return lines

def process_wrapper(args):
    """
    Wrapper function for article processing. Necessary for multiprocessing
    module support. See: http://docs.python.org/library/multiprocessing.html#multiprocessing.pool.multiprocessing.Pool.map
    """
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

def filter_apriori_input(occur_filename, output_filename, entity_type=Idea,
                         doc_terms=None):
    #select terms
    terms = select_terms(entity_type)
    Session.expunge_all()
    Session.close()

    lines = dm.prepare_apriori_input(occur_filename, terms, doc_terms)
    
    with open(output_filename, 'w') as f:
        f.writelines(lines)

def doc_terms_list():
    articles = Session.query(Entity)
    articles = articles.filter(Entity.sep_dir!=None)
    articles = articles.filter(Entity.sep_dir!='')
    articles = articles.all()
   
    doc_terms = defaultdict(list)

    for entity in articles:
        doc_terms[entity.sep_dir].append(entity)
    
    return doc_terms

def complete_mining(entity_type=Idea, filename='graph.txt', root='./',
                    corpus_root='corpus/', update_entropy=False,
                    update_occurrences=False, update_db=False): 
    occur_filename = os.path.abspath(root + "occurrences.txt")
    graph_filename = os.path.abspath(root + "graph-" + filename)
    edge_filename = os.path.abspath(root + "edge-" + filename)
    sql_filename = os.path.abspath(root + "sql-" + filename)

    doc_terms = doc_terms_list()

    if update_occurrences:
        print "processing articles..."
        process_articles(entity_type, occur_filename, corpus_root=corpus_root)

    print "filtering occurrences..."
    filter_apriori_input(
        occur_filename, graph_filename, entity_type, doc_terms)

    print "running apriori miner..."
    dm.apriori(graph_filename, edge_filename)
    
    print "processing edges..."
    edges = dm.process_edges(
        graph_filename, edge_filename, occur_filename, doc_terms)
    ents = dm.calculate_node_entropy(edges)
    edges = dm.calculate_edge_weight(edges, ents)
    
    print "creating sql files..."

    with open(sql_filename, 'w') as f:
        for edge, props in edges.iteritems():
            ante,cons = edge
            row = "%s::%s" % edge
            row += ("::%(confidence)s::%(jweight)s::%(weight)s"
                    "::%(occurs_in)s\n" % props)
            f.write(row)

    if update_entropy:
        print "updating term entropy..."

        for term_id, entropy in ents.iteritems():
            term = Session.query(Idea).get(term_id)
            if term:
                term.entropy = entropy

        Session.flush()
        Session.commit()
        Session.close()

    if update_db:
        print "updating the database..."
        update_graph(entity_type, sql_filename)


def update_graph(entity_type, sql_filename):
    """
    Performs a complete update of the database graph information, adding
    jweight, entropy and occurrence data from the sql file generated by
    complete_mining. This will remove ALL previous graph data.
    """
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
    TRUNCATE TABLE %(table)s;
    """ % {'filename' : sql_filename, 'table' : table })
    
    print "inserting new graph information"
    connection.execute("""
    SET foreign_key_checks=0;
    LOCK TABLES %(table)s WRITE;
    LOAD DATA INFILE '%(filename)s'
    INTO TABLE %(table)s
    FIELDS TERMINATED BY '::'
    (ante_id, cons_id, confidence, jweight, weight, occurs_in);
    UNLOCK TABLES;
    SET foreign_key_checks=1;
    """ % {'filename' : sql_filename, 'table' : table })
    Session.close()

def mine_article(article, entity_type=Idea, filename='graph.txt', root='./',
                 corpus_root='corpus/', update_entropy=False,
                 update_occurrences=False, update_db=False): 
    """
    Performs the data mining for a single article. Does not generate edge data
    using the frequent itemset mining algorithm or term entropy. 
    """
    logging.info("mining article: %s" % article)

    occur_filename = os.path.abspath(
        os.path.join(inpho.corpus.occur_path, article))
    sql_filename = os.path.abspath(
        os.path.join(inpho.corpus.sql_path, article))

    doc_terms = doc_terms_list()
   
    print "processing " + article + "..."
    process_article(article, entity_type=entity_type,
                    output_filename=occur_filename, corpus_root=corpus_root)

    # This will create a python dictionary of dictionary from the occur file.
    occurrences = dm.occurs_in(occur_filename, doc_terms)

    update_partial_graph(entity_type, occurrences)

def update_partial_graph(entity_type, occurrences):
    """
    Takes an entity type and a SQL filename and only updates part of the graph.
    For use with single article statistical information.
    """
    raise NotImplementedError

    # Import SQL statements
    if entity_type == Idea:
        table = "idea_graph_edges"
        type = IdeaGraphEdge
    elif entity_type == Thinker:
        table = "thinker_graph_edges"
        type = ThinkerGraphEdge
    else:
        table = "idea_thinker_graph_edges"
        type = IdeaThinkerGraphEdge

    edges = Session.query(type)
    # filter edges query to only the key term

    for ante, occurs in occurrences.iteritems():
        for cons, occurs_in in occurs.iteritems():
            # select the proper edge from result set
            # if edge does not exist, create it and add to session
            
            #update edge
            edge.occurs_in = occurs_in

    # commit changes
    Session.commit()

if __name__ == "__main__":
    # grab the corpus path
    import inpho.corpus
    corpus_root = inpho.corpus.path
    
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.set_defaults(type='all',
                        mode='complete',
                        update_entropy=False,
                        update_occurrences=False,
                        update_db=False,
                        article=None)
    parser.add_argument("-a", "--all",
                        action="store_const",
                        dest='type',
                        const='all',
                        help="mine all edges [default]")
    parser.add_argument("-i", "--idea",
                        action="store_const",
                        dest='type',
                        const='idea',
                        help="mine only idea-idea edges")
    parser.add_argument("-t", "--thinker",
                        action="store_const",
                        dest='type',
                        const='thinker',
                        help="mine only thinker-thinker edges")
    parser.add_argument("--complete",
                        action="store_const",
                        dest='mode',
                        const='complete',
                        help="complete data mining process [default]")
    parser.add_argument("--update-db",
                        action="store_true",
                        dest='update_db',
                        help="updates the database with results")
    parser.add_argument("--entropy",
                        action="store_true",
                        dest='update_entropy',
                        help="data mining, with entropy updates")
    parser.add_argument("--with-occur",
                        action="store_true",
                        dest='update_occurrences',
                        help="data mining, with occurrence file generation")
    parser.add_argument("--occur",
                        action="store_const",
                        dest='mode',
                        const='occur',
                        help="occurrence file generation")
    parser.add_argument("--load",
                        action="store_const",
                        dest='mode',
                        const='load',
                        help="load data from sql files")
    parser.add_argument("--new",
                        action="store_const",
                        dest='mode',
                        const='new_entries',
                        help="print a list of new entries")
    parser.add_argument("--categories",
                        action="store_const",
                        dest='mode',
                        const='categories',
                        help="print a list of categories")
    parser.add_argument("--entry",
                        dest='article',
                        help="process a single article")
    options = parser.parse_args()

    filename_root = options.type

    entity_type = Entity
    if options.type == 'idea':
        entity_type = Idea
    elif options.type == 'thinker':
        entity_type = Thinker
   
    # single article parsing?
    if options.article is not None:
        options.mode = 'single'

    # pick the right action
    if options.mode == 'complete':
        complete_mining(entity_type, 
                        filename=filename_root, 
                        corpus_root=corpus_root, 
                        update_entropy=options.update_entropy,
                        update_occurrences=options.update_occurrences,
                        update_db=options.update_db)
    elif options.mode == 'single':
        mine_article(options.article,
                     entity_type,
                     filename=filename_root, 
                     corpus_root=corpus_root, 
                     update_entropy=options.update_entropy,
                     update_occurrences=options.update_occurrences,
                     update_db=options.update_db)
    elif options.mode == 'load':
        sql_filename = os.path.abspath(corpus_root + "sql-" + filename_root)
        update_graph(entity_type, sql_filename)
    elif options.mode == 'occur':
        occur_filename = os.path.abspath("./occurrences.txt")
        process_articles(entity_type, occur_filename, corpus_root=corpus_root)
    elif options.mode == 'new_entries':
        fuzzymatch_new()
    elif options.mode == 'categories':
        for article, category in get_categories().iteritems():
            print "%s::%s" % (article, category)
