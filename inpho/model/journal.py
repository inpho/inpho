import os.path

from inpho.model.entity import Entity

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
    
    def url(self, filetype='html', action='view'):
        return url(controller='journal', action=action, id=self.ID, filetype=filetype)

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
