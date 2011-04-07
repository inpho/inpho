from inpho.model import Entity

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

    def url(self, filetype='html', action='view'):
        return url(controller='school_of_thought', action=action, id=self.ID, filetype=filetype)
