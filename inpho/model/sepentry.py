from sqlalchemy.ext.associationproxy import association_proxy

class SEPEntry(object):
    """
    SEPEntry object for ORM, is initializable
    """
    def __init__(
        self,
        title,
        sep_dir,
        published=False,
        status='Unknown',
    ):
        self.title   = title
        self.sep_dir   = sep_dir
        self.published  = published
        self.status = status

    fuzzymatches = association_proxy('fmatches', 'entityID')
        
    def __repr__(self):
        return "SEPEntry(%(title)s)" % self.__dict__

class Fuzzymatch(object):
    def __init__(self, entityID):
        self.entityID = entityID
