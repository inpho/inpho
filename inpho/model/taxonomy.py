import os.path

from inpho.model.entity import Entity

class Node(Entity):
    def __repr__(self):
        return '<Node %s: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')
    
    def url(self, filetype='html', action='view'):
        return url(controller='taxonomy', action=action, id=self.ID, filetype=filetype)

    def json_struct(self, sep_filter=True, limit=10, extended=True):
        struct = { 'ID' : self.ID, 
                  'type' : 'node',
                  'label' : self.label, 
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'idea' : self.idea.ID,
                  'children' : [child.ID for child in self.children],
                  'parent' :  self.parent.ID if self.parent else 0 })
        return struct

    def path_to_root(self):
        """Returns the direct path to the root node."""
        path = [self.parent]
        curParent = self.parent

        while curParent:
            curParent = curParent.parent
            path.append(curParent)

        return path

    # TODO: switch loop to an enumerate!
    def paths_to_root(self, max=False):
        """Returns a list of paths and alternate paths to root using links"""
        direct = self.path_to_root()
        paths = [direct]

        # iterate through alternates
        for i,n in enumerate(direct):
            if not n:
                break
            # build list of alternative nodes for that idea
            alts = [a for a in n.idea.nodes if a not in direct]

            # build list of links from that idea
            links = n.idea.links
            for l in links:
                alts.extend([node for node in l.nodes if node not in direct])
    
            # iterate through alternatives and append to list of paths
            for alt in alts:
                p = direct[:i+1]
                p.append(alt)
                p.extend(alt.path_to_root())
                if (not max or len(p) <= max) and p not in paths:
                    paths.append(p)

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



class Instance(object):
    pass
