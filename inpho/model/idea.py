from inpho.model.entity import Entity
import os.path

class Idea(Entity):
    """
    Simple Idea class, has custom definitions for representation strings.
    """
    def __init__(self, label):
        self.label = label
        self.searchstring = label
        self.searchpattern = '(%s)' % label

    def __repr__(self):
        return '<Idea %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def url(self, filetype='html', action='view'):
        return url(controller='idea', action=action, id=self.ID, filetype=filetype)

    def json_struct(self, sep_filter=True, limit=10, extended=True, graph=False, glimit=None):
        struct = { 'ID' : self.ID, 
                  'type' : 'idea',
                  'label' : self.label, 
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'nodes' : [node.ID for node in self.nodes],
                  'instances' : [ins.ID for ins in self.instances],
                  'classes' : [child.idea.ID for ins in self.nodes 
                                             for child in ins.children],
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
            search_string = search_string.replace("<u>", "\" \"")  #union
       #     search_string = replace(search_string, "in", "\" \"")   #union
            search_string = search_string.replace("<i>", "\" | \"") #disjunct
        
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
        nodes = self.nodes[:]
        if nodes:
            paths = map(lambda x: x.path_to_root(), nodes)
            best = min(paths, key=lambda x: len(x))
            return best

        # otherwise look at the instances
        nodes = []
        for i in self.instance_of:
            nodes.extend(i.nodes[:])

        if nodes:
            paths = map(lambda x: x.path_to_root(), nodes)
            best = min(paths, key=lambda x: len(x))
            return best

        raise Exception("Idea is not an instance or node")
        
    def paths_to_root(self,max=False):
        """Returns a list of paths and alternate paths to root using links"""
        nodes = self.nodes[:]
        for i in self.instance_of:
            nodes.extend(i.nodes[:])
        
        paths = [self.path_to_root()]
        npaths = map(lambda x: x.paths_to_root(), nodes)
        for n in npaths:
            if (not max or len(n) <= max) and n not in paths:
                paths.extend(n)
        return paths
	
    
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
    
    def shortest_path(self, node, alt_paths=True):
        path = self.path(self.path_to_root(), node.path_to_root())
        if not alt_paths:
            return path

        best = path
        for s in self.paths_to_root(len(best)):
            for n in node.paths_to_root(len(best)):
                path = self.path(s, n, len(best))
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
