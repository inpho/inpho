from inpho.model import Entity

#work classes
class Work(Entity):
    def __init__(self, label):
        self.label = label
        self.searchstring = label
        self.searchpattern = '(%s)' % label

    def __repr__(self):
        return '<Work %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype='html', action='view'):
        return url(controller='work', action=action, id=self.ID, filetype=filetype)
