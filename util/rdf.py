"""
Script to convert from InPhO data model to RDF triple store.
"""
import rdflib
from rdflib import Literal, Namespace
from rdflib.graph import ConjunctiveGraph as Graph

from inpho.model import *

from itertools import *

inpho = Namespace("http://inpho.cogs.indiana.edu/")
t = Namespace("http://inpho.cogs.indiana.edu/thinker/")
j = Namespace("http://inpho.cogs.indiana.edu/journal/")
u = Namespace("http://inpho.cogs.indiana.edu/user/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/TR/rdf-schema/#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
i = Namespace("http://inpho.cogs.indiana.edu/idea/")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
db = Namespace("http://dbpedia.org/")
dc = Namespace("http://purl.org/dc/elements/1.1/")

def make_graph():
    g = Graph()

    # add namespaces
    g.bind("inpho", "http://inpho.cogs.indiana.edu/")
    g.bind("thinker", "http://inpho.cogs.indiana.edu/thinker/")
    g.bind("journal", "http://inpho.cogs.indiana.edu/journal/")
    g.bind("foaf", "http://xmlns.com/foaf/0.1/")
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/TR/rdf-schema/#")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    g.bind("idea", "http://inpho.cogs.indiana.edu/idea/")
    g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    g.bind ("db", "http://dbpedia.org/")
    g.bind ("dc", "http://purl.org/dc/elements/1.1/")
    
    # user namespace currently doesn't exist?
    g.bind("user", "http://inpho.cogs.indiana.edu/user/")

    # OWL disjoints
    disjoint_objects = ["thinker", "journal", "idea", "user"]
    for a, b in combinations(disjoint_objects, 2):
        g.add((inpho[a], owl['disjointWith'], inpho[b]))
 
    g = populate_thinkers(g)
    g = populate_ideas(g)
    g = populate_journals(g)

    return g

def populate_thinkers(g):
    # Select all Thinkers
    thinkers = Session.query(Thinker).all()
    g.add((inpho['thinker'], rdf['type'], foaf['person']))
    
    for thinker in thinkers:
        g.add((t[str(thinker.ID)], rdf['type'], inpho['thinker']))
        g.add((t[str(thinker.ID)], foaf['name'], Literal(thinker.label)))
        
        g = populate_entity(g, thinker, t)
        
        if thinker.wiki:
            g.add((t[str(thinker.ID)], owl['sameAs'], db[thinker.wiki.decode('utf-8')]))

        for birth in thinker.birth_dates:
            g.add((t[str(thinker.ID)], inpho['birth_date'], Literal(repr(birth))))
        for death in thinker.death_dates:
            g.add((t[str(thinker.ID)], inpho['death_date'], Literal(repr(death))))
            
        for student in thinker.students:
            g.add((t[str(student.ID)], inpho['student'], t[str(thinker.ID)]))
        for teacher in thinker.teachers:
            g.add((t[str(teacher.ID)], inpho['teacher'], t[str(thinker.ID)]))
        for influence in thinker.influenced:
            g.add((t[str(influence.ID)], inpho['influenced'], t[str(thinker.ID)]))
        for influence in thinker.influenced_by:
            g.add((t[str(influence.ID)], inpho['influenced_by'], t[str(thinker.ID)]))

    return g

def populate_ideas(g):
    # Select all ConceptSchemes
    g.add((skos['conceptscheme'], skos['hasTopConcept'], inpho['idea']))

    #Select all Ideas
    ideas = Session.query(Idea).all()
    g.add((inpho['idea'], rdfs['subClassOf'], skos['Concept']))
    g.add((inpho['idea'], skos['exactMatch'], db['concept'])) 

    for idea in ideas:
        g = populate_entity(g, idea, i)
        g.add((i[str(idea.ID)], rdf['type'], inpho['idea']))
        for instance in idea.instances:
            g.add((i[str(idea.ID)], skos['broader'], i[str(instance.ID)]))
        for node in idea.nodes:
            for child in node.children:
                g.add((i[str(idea.ID)], skos['broader'], i[str(child.idea.ID)]))

    return g

def populate_users(g):
    users = Session.query(User).all()
    g.add((inpho['user'], rdf['type'], foaf['Person']))
    g.add((inpho['expert_user'], rdfs['subClassOf'], inpho['user']))
    g.add((inpho['turk_user'], rdf['type'], foaf['Person']))
    g.add((inpho['admin'], rdfs['subClassOf'], inpho['user']))
    for user in users:
        g.add((u['u' + str(user.ID)], rdf['type'], inpho['user']))

    return g

def populate_journals(g):
    # Select all Journals
    journals = Session.query(Journal).all()
    for journal in journals:
        g.add((j[str(journal.ID)], rdf['type'], inpho['journal']))
        g = populate_entity(g, journal, j)

        if journal.URL:
            g.add((j[str(journal.ID)], rdf['about'], Literal(journal.URL)))
            g.add((j[str(journal.ID)], foaf['homepage'], Literal(journal.URL)))
        if journal.language:
            g.add((j[str(journal.ID)], dc['language'], Literal(journal.language)))

    return g

def populate_entities(g):
    # Select all Entities
    entities = Session.query(Entity).all()
    g.add((inpho['entity'], rdf['type'], owl['Thing']))
    for entity in entities:
        g.add((e[str(entity.ID)], rdf['type'], inpho['entity']))
        g.add((e[str(entity.ID)], skos['prefLabel'], Literal(entity.label)))
        if entity.created_by:
            g.add((e[str(entity.ID)], inpho['provenance'], Literal(entity.created_by)))
            g.add((e[str(entity.ID)], dc['creator'], Literal(entity.created_by)))
        if entity.created:
            g.add((e[str(entity.ID)], dc['created'], Literal(entity.created)))
        for searchpattern in entity.searchpatterns:
            g.add((e[str(entity.ID)], skos['altLabel'], Literal(entity.label)))
    
    return g

def populate_entity(g, entity, type):
    g.add((type[str(entity.ID)], skos['prefLabel'], Literal(entity.label)))
    g.add((type[str(entity.ID)], rdfs['label'], Literal(entity.label)))
    g.add((type[str(entity.ID)], foaf['name'], Literal(entity.label)))
    if entity.created_by:
        g.add((type[str(entity.ID)], inpho['provenance'], Literal(entity.created_by)))
        g.add((type[str(entity.ID)], dc['creator'], Literal(entity.created_by)))
    if entity.created:
        g.add((type[str(entity.ID)], dc['created'], Literal(entity.created)))
    for searchpattern in entity.searchpatterns:
        g.add((type[str(entity.ID)], skos['altLabel'], Literal(entity.label)))

    return g

# serialization format argument parser
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="determines RDF serialization format")
    parser.add_argument('-f', '--format', 
                        dest='serialization', 
                        help='set the serialization format', 
                        choices=['n3', 'nt', 'pretty-xml', 'trix', 'turtle', 'xml'], 
                        default='n3')
    args = parser.parse_args()
    g = make_graph()
    with open("out_" + str(args.serialization) + ".rdf", "w") as f:
        f.write(g.serialize(format=args.serialization))
