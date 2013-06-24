"""
inpho.model.idea contains the SQLAlchemy objects representing concepts in an
ontology. It also contains the idea evaluation objects.

By executing this file as a script with the ``--export`` flag and an optional
``-f`` flag specifying an output filename, a list of all concepts in the
database is constructed.
"""

from inpho.lib import rdf
from inpho.model.entity import Entity
import os.path
import inpho.helpers

class Idea(Entity):
    """
    Simple Idea class, has custom definitions for representation strings.
    """
    def __init__(self, label, sep_dir=None):
        self.label = label
        self.searchstring = label
        self.searchpattern = '(%s)' % label
        self.sep_dir = sep_dir

    def __repr__(self):
        return '<Idea %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype=None, action=None, id2=None):
        return inpho.helpers.url(controller="idea", id=self.ID, action=action, 
                                 id2=id2, filetype=filetype)

    # Triple Generation Code
    def rdf(self, graph):
        graph.add((rdf.inpho['idea'], rdf.rdf['type'], rdf.foaf['person']))
        graph.add((rdf.inpho['idea'], rdf.rdfs['subClassOf'], rdf.inpho['entity']))
        
        graph.add((rdf.t['t' + str(self.ID)], rdf.rdf['type'], rdf.inpho['idea']))
        graph.add((rdf.t['t' + str(self.ID)], rdf.foaf['name'], rdf.Literal(self.label)))
        graph.add((rdf.t['t' + str(self.ID)], rdf.owl['sameAs'], rdf.e['e' + str(self.ID)]))
        
        return graph

    # Make graph of Triples
    def graph(self, graph=None):
        if graph == None:
            graph = rdf.make_graph()

        graph = self.rdf(graph)

        return graph

    def json_struct(self, sep_filter=True, limit=10, extended=True, graph=False, glimit=None):
        struct = { 'ID' : self.ID, 
                  'type' : 'idea',
                  'label' : inpho.helpers.titlecase(self.label), 
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'instances' : [ins.ID for ins in self.instances],
                  'links' : [ins.ID for ins in self.links]})
            if sep_filter:
                struct.update({
                  'hyponyms' : [ins.ID for ins in
                  self.hyponyms.filter(Entity.sep_dir != '')[0:limit-1] ],
                  'occurrences' : [ins.ID for ins in self.occurrences.filter(Entity.sep_dir != '')[0:limit-1] ],
                  'related' : [ins.ID for ins in self.related.filter(Entity.sep_dir != '')[0:limit-1] ],
                  'related_thinkers' : [ins.ID for ins in self.related_thinkers.filter(Entity.sep_dir != '')[0:limit-1] ]})
            else:
                struct.update({
                  'hyponyms' : [ins.ID for ins in self.hyponyms[0:limit-1] ],
                  'occurrences' : [ins.ID for ins in self.occurrences[0:limit-1] ],
                  'related' : [ins.ID for ins in self.related[0:limit-1] ],
                  'related_thinkers' : [ins.ID for ins in self.related_thinkers[0:limit-1] ]})
        if graph:
            struct.update({
                'entropy' : self.entropy,
                'it_in' : [edge.json_struct() 
                               for edge in self.it_in_edges[:glimit]],
                'it_out' : [edge.json_struct() 
                               for edge in self.it_out_edges[:glimit]],
                'ii_in' : [edge.json_struct() 
                               for edge in self.ii_in_edges[:glimit]],
                'ii_out' : [edge.json_struct() 
                               for edge in self.ii_out_edges[:glimit]],
                })

        return struct

    def web_search_string(self):
        # generates search string for search engines
        search_string = self.searchstring
        if (self.searchstring.find("<u>") >= 0) or (self.searchstring.find("<i>") >= 0): 
            search_string = search_string.replace("<u>", "\" + \"")  #union
            search_string = search_string.replace("<i>", "\" | \"")  #disjunct
        
        search_string = "\"" + search_string + "\""

        return search_string

    def get_filename(self, corpus_path=None):
        if corpus_path and self.sep_dir:
            filename = os.path.join(corpus_path, self.sep_dir,'index.html')
            if not os.path.exists(filename):
                filename = None
        else:
            filename = None

        return filename
    
    def path_to_root(self):
        """Returns the shortest direct path to the root node."""
        return min(self.paths_to_root(), key=len)
        
    def paths_to_root(self,max=False):
        """Returns a list of paths and alternate paths to root using links"""
        
        if not self.instance_of:
            # terminate recursion
            return [[self]]
        else:
            paths = []
            for parent in self.instance_of:
                paths.extend(parent.paths_to_root())
            # TODO: Insert links as well
            for path in paths:
                path.insert(0, self)
            return paths

        # TODO: Handle cases with 0 paths to root
	
    
    @staticmethod
    def path_length(path1, path2, best=20):
        dist = 0
        dist2 = 0
        for s in path1:
            dist += 1
            dist2 = 0
            for n in path2:
                if n == s:
                    return dist + dist2
                dist2 += 1
                
                if dist+dist2 > best:
                    return False
        
        raise Exception("Path not found")

    @staticmethod
    def path(path1, path2, stop=False):
        path = []
        for s in path1:
            path.append(s)
            for j,n in enumerate(path2):
                if stop and len(path)+j > stop:
                    return False

                if n == s:
                    p2 = path2[:j]
                    p2.reverse()
                    path.extend(p2)
                    return path

        raise Exception("Path not found")
    
    def shortest_path(self, other, alt_paths=True):
        path = self.path(self.path_to_root(), other.path_to_root())
        if not alt_paths:
            return path

        best = path
        for s in self.paths_to_root(len(best)):
            for o in other.paths_to_root(len(best)):
                path = self.path(s, o, len(best))
                if path and len(path) < len(best):
                    best = path
        
        return best 

    def get_related_idea_ids(self, n=10, recur=0):    
        if n:
            ns = self.related[:n]
        else:
            ns = self.related[:]
        ids = set()
        ids.add(self.ID)
        for node in ns:
            ids.add(node.ID)

        if recur:
            for node in ns:
                ids2 = node.get_related_idea_ids(n/2, recur-1)
                for id in ids2:
                    ids.add(id)
        return ids

class IdeaEvaluation(object):
    """
    Idea Evaluation object for ORM, is initializable
    """
    def __init__(self, id, id2, uid, relatedness=-1, generality=-1, hyperrank=-1, hyporank=-1):
        self.ante_id = id
        self.cons_id = id2
        self.uid = uid
        self.relatedness = relatedness
        self.generality = generality
        self.hyperrank = hyperrank
        self.hyporank = hyporank

class AnonIdeaEvaluation(object):
    """
    Idea Evaluation object for ORM, is initializable
    """
    def __init__(self, id, id2, ip, relatedness=-1, generality=-1, hyperrank=-1, hyporank=-1):
        self.ante_id = id
        self.cons_id = id2
        self.ip = ip
        self.relatedness = relatedness
        self.generality = generality
        self.hyperrank = hyperrank
        self.hyporank = hyporank

# Export functionality
if __name__ == '__main__':
    from argparse import ArgumentParser
    from codecs import open
    import os.path
    import sys

    # NOTE: despite Idea being defined in this module, it must be reimported
    # from inpho.model so that it is properly bound to the model.
    from inpho.model import Session, Idea

    # configure argument parser
    parser = ArgumentParser(description='CLI for Idea objects.')
    parser.add_argument('--export', dest='export', action='store_true')
    parser.add_argument('-f', dest='filename', action='store')

    # parse arguments
    args = parser.parse_args()

    # if export mode is enabled, export the IDs and labels
    if args.export:
        # write to file, or to standard out
        if args.filename:
            f = open(args.filename, 'w', encoding='utf-8')
        else: 
            f = sys.stdout

        for id, label in Session.query(Idea.ID, Idea.label).all():
            # NOTE: can be rewritten with csv module, but unicode issues
            # surround us on all sides...
            print >>f, "%s,%s" % (id, label)

