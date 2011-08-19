import re
""" 
A taxonomy is a directed graph consisting of *instances* and *links*.

The optional "spine" specifies a collection of hand-coded instances, which
may be ommitted from the usual taxonomy evaluation techniques.
"""

class Node(object):
    def __init__(self, value=None, spine=None):
        self.value = value
        self.spine = spine
        self.parent = None
        self._children = set()
        self.links = set()

    def __repr__(self):
        return 'Node %s' % (self.value)

    @property
    def children(self):
        return frozenset(self._children)

    @property
    def edges(self):
        edges = [(self.value, node.value) for node in self.children]
        for node in self.children:
            edges.extend(node.edges)
        return edges
    
    @property
    def root(self):
        return self.parent.root if self.parent else self

    def graft(self, child):
        self._children.add(child)
        child.parent = self
        return self

    def prune(self, child):
        self._children.remove(child)
        child.parent = None
        return child

    def fragment(self):
        self.parent._children.remove(self)
        self.parent = None
        return self

    def siblings(self):
        siblings = list(self.parent.children)
        siblings.remove(self)
        return siblings

    def search(self, needle):
        if self.value == needle:
            return self
        
        for node in self.children:
            result = node.search(needle)
            if result:
                return result
        
        return False

