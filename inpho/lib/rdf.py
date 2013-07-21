import rdflib
from rdflib import Literal, Namespace
from rdflib.graph import ConjunctiveGraph as Graph

from itertools import *

# add namespaces
inpho = Namespace("http://inpho.cogs.indiana.edu/")
t = Namespace("http://inpho.cogs.indiana.edu/thinker/")

# user namespace currently doesn't exist?
u = Namespace("http://inpho.cogs.indiana.edu/user/")
e = Namespace("http://inpho.cogs.indiana.edu/entity/")
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

    g.bind("inpho", "http://inpho.cogs.indiana.edu/")
    g.bind("thinker", "http://inpho.cogs.indiana.edu/thinker/")

    g.bind("user", "http://inpho.cogs.indiana.edu/user/")
    g.bind("entity", "http://inpho.cogs.indiana.edu/entity/")
    g.bind("foaf", "http://xmlns.com/foaf/0.1/")
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/TR/rdf-schema/#")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    g.bind("idea", "http://inpho.cogs.indiana.edu/idea/")
    g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    g.bind ("db", "http://dbpedia.org/")
    g.bind ("dc", "http://purl.org/dc/elements/1.1/")

    return g
