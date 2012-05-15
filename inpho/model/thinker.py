import os.path

from inpho.model.entity import Entity
from inpho.model.idea import Idea
import inpho.helpers

from sqlalchemy.ext.associationproxy import association_proxy

class Thinker(Entity):
    """
    Simple Thinker class, has custom definitions for representation strings.
    """
    def __init__(self, name, **kwargs):
        self.label = name
        self.name = name
        self.searchstring = name
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __repr__(self):
        return '<Thinker %s: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype=None, action=None, id2=None):
        return inpho.helpers.url(controller="thinker", id=self.ID, 
                                 action=action, id2=id2, filetype=filetype)

    aliases = association_proxy('alias', 'value')

    def json_struct(self, sep_filter=True, limit=10,extended=True,graph=False,glimit=None):
        struct = { 'ID' : self.ID, 
                  'type' : 'thinker',
                  'label' : self.label, 
                  'sep_dir' : self.sep_dir,
                  'wiki' : self.wiki,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'aliases' : self.aliases,
                  'birth' : {'year' : self.birth_year,
                             'month' : self.birth_month,
                             'day' : self.birth_day},
                  'birth_string' : self.birth_string,
                  'death' : {'year' : self.death_year,
                             'month' : self.death_month,
                             'day' : self.death_day},
                  'death_string' : self.death_string,
                  'nationalities' : [n.name for n in self.nationalities] ,
                  'professions' : [p.name for p in self.professions] ,
                  'teachers' : [t.ID for t in self.teachers],
                  'students' : [s.ID for s in self.students],
                  'influenced_by' : [i.ID for i in self.influenced_by],
                  'influenced' : [i.ID for i in self.influenced]})
            if sep_filter:
                struct.update({
                    'related_ideas' : [i.ID for i in
                            self.related_ideas.filter(Idea.sep_dir != '')[:limit-1]]})
            else:
                struct.update({
                    'related_ideas' : [i.ID for i in self.related_ideas[:limit-1]]})


        if graph:
            struct.update({
                'it_in' : [edge.json_struct() 
                               for edge in self.it_in_edges[:glimit]],
                'it_out' : [edge.json_struct() 
                               for edge in self.it_out_edges[:glimit]],
                'tt_in' : [edge.json_struct() 
                               for edge in self.tt_in_edges[:glimit]],
                'tt_out' : [edge.json_struct() 
                               for edge in self.tt_out_edges[:glimit]],
                })

        return struct

    def birth_sd(self):
        return SplitDate(self.birth_year, self.birth_month, self.birth_day)
    def death_sd(self):
        return SplitDate(self.death_year, self.death_month, self.death_day)

    @property
    def birth_string(self):
        return str(self.birth_sd())

    @property
    def death_string(self):
        return str(self.death_sd())
    
    def get_filename(self, corpus_path=None):
        if corpus_path and self.sep_dir:
            filename = os.path.join(corpus_path, self.sep_dir,'index.html')
            if not os.path.exists(filename):
                filename = None
        else:
            filename = None

        return filename

from datetime import datetime, date
import re
class SplitDate(object):
    """ For use with ``sqlalchemy.orm.composite`` to represent our three-column
    (month/date/year) dates and transform them into Python ``date`` objects.
    """
    def __init__(self, year, month, day):
        try:
            self.year = int(year)
        except:
            yearera = re.findall("(\d+) (BC|AD|BCE|CE)", str(year))
            if yearera:
                year = yearera[0][0]
                era = yearera[0][1]
                if era in ('BC', 'BCE'):
                    self.year = int(year)*-1
                elif era in ('AD', 'CE'):
                    self.year = int(year)
            else:
                self.year = None

        try:
            self.month = int(month)
        except:
            try:
                self.month = datetime.strptime(month, "%B").month
            except:
                self.month = None

        try:
            self.day = int(day)
        except:
            self.day = None

    def __composite_values__(self):
        return self.year, self.month, self.day
    
    def __str__(self):
        if (self.year and self.year > 0):
            era = "CE"
        else:
            era = "BCE"
        if (self.year and self.month and self.day):
            return "%4d-%2d-%2d %s" % (abs(self.year), self.month, self.day, 
                                       era)
        elif (self.year and self.month):
            return "%4d-%2d %s" % (abs(self.year), self.month, era)
        elif self.year:
            return "%4d %s" % (abs(self.year), era)
        else:
            return "%s" % (era)

    # weird bug in Python: bool(x) --> x.__nonzero__() instead of x.__bool__()
    # http://mail.python.org/pipermail/python-3000/2006-November/004524.html
    def __nonzero__(self):
        if self.year is not None or self.month is not None or self.day is not None:
            return True
        else:
            return False

    def __eq__(self, other):
        return other and self.year == other.year and self.month == other.month and self.day == other.day
    


class Nationality(object):
    pass

class Profession(object):
    pass

class Alias(object):
    pass

class ThinkerEvaluation(object):
    """
    Thinker Evaluation object for ORM, is initializable
    """
    def __init__(
        self,
        ante_id=None,
        cons_id=None,
        uid=None,
        degree=-1
    ):
        self.ante_id = ante_id
        self.cons_id = cons_id
        self.uid = uid
        self.degree = degree

class ThinkerTeacherEvaluation(ThinkerEvaluation):
    pass

class ThinkerInfluencedEvaluation(ThinkerEvaluation):
    pass
