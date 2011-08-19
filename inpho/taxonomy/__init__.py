from collections import defaultdict
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

def from_dlv(filename):
    """
    Function to return a taxonomy from the specified DLV output file.
    """
    # build regex for instance and link search
    regex_class = re.compile("class\(i(\d+)\)")
    regex_ins = re.compile("[ins|isa]\(i(\d+),i(\d+)\)")
    regex_links = re.compile("link\(i(\d+),i(\d+)\)")
 
    with open(filename) as f:
        dlv = f.read()

        classes = frozenset(regex_class.findall(dlv))
        instances = frozenset(regex_ins.findall(dlv))
        links = frozenset(regex_links.findall(dlv))

    nodes = defaultdict(Node)
    root = Node("Philosophy", spine=True)

    for child, parent in instances:
        nodes[parent].graft(nodes[child])

    for target, source in links:
        nodes[source].links.add(nodes[target])

    for key,node in nodes.iteritems():
        node.value = key
        if node.value in classes:
            node.spine = True
        if node.parent is None:
            root.graft(node)

    return root
