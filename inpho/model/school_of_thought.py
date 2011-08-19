from inpho.model import Entity
import inpho.helpers

#group classes
class SchoolOfThought(Entity):
    def __init__(self, label):
        self.label = label
        self.searchstring = label
        self.searchpattern = '(%s)' % label

    def __repr__(self):
        return '<School of Thought %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype=None, action=None):
        return inpho.helpers.url(controller="school_of_thought", id=self.ID, 
                                 action=action, filetype=filetype)
