import os.path

from inpho.model.entity import Entity
import inpho.helpers

from sqlalchemy.ext.associationproxy import association_proxy

class Journal(Entity):
    """
    Simple Journal class, has custom definitions for representation strings.
    """
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __repr__(self):
        return '<Journal %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label
    
    def url(self, filetype=None, action=None):
        return inpho.helpers.url(controller="journal", id=self.ID, 
                                 action=action, filetype=filetype)

    abbrs = association_proxy('abbreviations', 'value')
    queries = association_proxy('query', 'value')

    def json_struct(self, sep_filter=True, limit=10, extended=True):
        struct = { 'ID' : self.ID, 
                  'type' : 'journal',
                  'label' : self.label,
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'website' : self.URL,
                  'language' : self.language,
                  'abbrs' : self.abbrs,
                  'queries' : self.queries,
                  'openAccess' : self.openAccess,
                  'active' : self.active,
                  'student' : self.student,
                  'ISSN' : self.ISSN })
        return struct

class Abbr(object):
    def __init__(self, value):
        self.value = value

class SearchQuery(object):
    def __init__(self, value):
        self.value = value
