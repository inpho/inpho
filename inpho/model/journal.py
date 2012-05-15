from httplib import HTTPException
import logging
import os.path
import time
from urllib import quote_plus

import inpho.helpers
from inpho.lib.url import URLopener
from inpho.model.entity import Entity

from sqlalchemy.ext.associationproxy import association_proxy

class Journal(Entity):
    """
    Simple Journal class, has custom definitions for representation strings.
    """
    def __init__(self, name, **kwargs):
        self.label = name
        self.name = name
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __repr__(self):
        return '<Journal %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label
    
    def url(self, filetype=None, action=None, id2=None):
        return inpho.helpers.url(controller="journal", id=self.ID, id2=id2,
                                 action=action, filetype=filetype)

    abbrs = association_proxy('abbreviations', 'value')
    queries = association_proxy('query', 'value')

    def check_url(self):
        """ Verifies the journal still has a good URL. """
        # if journal does not have a URL, return None which is False-y
        if not self.URL:
            return None

        # attempt to open the URL, capture exceptions as failure
        try:
            request = URLopener().open(self.URL)
        except (IOError, HTTPException) as e:
            logging.warning("URL failed w/exception! [%s] %s" % (self.URL, e))
            return False

        # Get HTTP status code
        status = request.getcode()

        # If there is a redirect, fix the url
        if status == 302:
            self.URL = request.geturl()

        # Update the last accessed time
        if status <= 307:
            self.last_accessed = time.time()
            return True
        else:
            return False

    @property
    def last_accessed_str(self, format="%x %X %Z"):
        return time.strftime(format, time.gmtime(self.last_accessed))

    @property
    def ISSN_google_url(self):
        google = "http://www.google.com/search?q="
        google += quote_plus("%s %s" % (self.label.encode("utf-8"), self.ISSN))
        return google 

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
