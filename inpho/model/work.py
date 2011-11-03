from inpho.model import Entity
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

    def url(self, filetype=None, action=None):
        return inpho.helpers.url(controller="work", id=self.ID, action=action, 
                                 filetype=filetype)
