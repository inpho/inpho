import os.path
from sqlalchemy.orm import subqueryload
from sqlalchemy import and_, or_, not_

from inpho.model import Idea, Thinker, Entity, Session 

class Term(object):
    def __init__(self, label, searchpatterns=[]):
        self.label = label
        self.searchpatterns = searchpatterns

def inpho_terms(entity_type=Idea):
    # process entities
    ideas = Session.query(entity_type)
    ideas = ideas.options(subqueryload('_spatterns'))
    # do not process Nodes or Journals
    ideas = ideas.filter(and_(Entity.typeID!=2, Entity.typeID!=4))
    ideas = ideas.all()
    
    Session.expunge_all()
    Session.close()
    return ideas

