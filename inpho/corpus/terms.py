import os.path
import pickle

from sqlalchemy.orm import subqueryload
from sqlalchemy import and_, or_, not_

from inpho.model import Idea, Thinker, Entity, Session 

class Term(object):
    __slots__ = ['label', 'searchpatterns', 'source', 'ID']
        
    def __init__(self, label, searchpatterns=[], source=None, ID=None):
        self.label = label
        self.searchpatterns = searchpatterns
        
        self.source = source
        self.ID = ID

    def __repr__(self):
        if self.source and self.ID is not None:
            return '<Term %s-%d: %s>' % (self.source, self.ID, self.label.encode('utf-8'))
        else:
            return '<Term: %s>' % (self.source, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

def inpho_terms(entity_type=Idea):
    # process entities
    ideas = Session.query(entity_type)
    ideas = ideas.options(subqueryload('_spatterns'))
    # do not process Nodes or Journals
    ideas = ideas.filter(and_(Entity.typeID!=2, Entity.typeID!=4))
    ideas = ideas.all()

    Session.expunge_all()
    Session.close()

    ideas = [Term(idea.label, idea.searchpatterns, 'InPhO', idea.ID)
                 for idea in ideas]
    return ideas

def graph_terms(filename, source_name=None):
    with open(filename, 'r') as f:
        graph = pickle.load(f)

    terms = [Term(data['label'], source=source_name)
                 for id, data in graph.nodes_iter(data=True)]
    return terms
