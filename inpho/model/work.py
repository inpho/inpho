from inpho.model import Entity
from inpho.lib import rdf
import inpho.helpers

#work classes
class Work(Entity):
    def __init__(self, label, **kwargs):
        self.label = label
        self.searchstring = label
        self.searchpattern = '(%s)' % label
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)


    def __repr__(self):
        return '<Work %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype=None, action=None, id2=None):
        return inpho.helpers.url(controller="work", id=self.ID, action=action, 
                                 id2=id2, filetype=filetype)
    # Triple Generation Code
    def rdf(self, graph):
        graph.add((rdf.inpho['work'], rdf.rdf['type'], rdf.foaf['person']))
        graph.add((rdf.inpho['work'], rdf.rdfs['subClassOf'], rdf.inpho['entity']))
        
        graph.add((rdf.t['t' + str(self.ID)], rdf.rdf['type'], rdf.inpho['work']))
        graph.add((rdf.t['t' + str(self.ID)], rdf.foaf['name'], rdf.Literal(self.label)))
        graph.add((rdf.t['t' + str(self.ID)], rdf.owl['sameAs'], rdf.e['e' + str(self.ID)]))
        
        return graph

    # Make graph of Triples
    def graph(self, graph=None):
        if graph == None:
            graph = rdf.make_graph()

        graph = self.rdf(graph)

        return graph


