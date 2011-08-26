from collections import defaultdict
import re

class Node(object):
    """
    Class to represent an InPhO taxonomy
    """
    def __init__(self, value=None, spine=None):
        self.value = value
        self.spine = spine
        self.parent = None
        self._children = set()
        self.links = set()

    def __repr__(self):
        return 'Node %s' % (self.value)

    def __iter__(self):
        return self.next()
 
    def next(self):
        """ A recursive generator that prints the depth-first traversal. """
        yield self 
        for child in self.children:
            for node in child:
                yield node

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
        """ Returns the root parent node. """
        return self.parent.root if self.parent else self

    def graft(self, child):
        """ Appends the Node as a child. """
        self._children.add(child)
        child.parent = self
        return self

    def prune(self, child):
        """ 
        Removes the given child Node. 
        Raises KeyError if child is not found in children.
        """
        self._children.remove(child)
        child.parent = None
        return child

    def fragment(self):
        """ 
        Removes this Node from its parent and returning a free-standing tree.
        """
        if self.parent is not None:
            return self.parent.prune(self)

    def siblings(self):
        """ Returns the list of siblings """
        siblings = list(self.parent.children)
        siblings.remove(self)
        return siblings

    def search(self, needle):
        """ Search the tree with root self for needle. """
        return self.search_dfs(needle)

    def search_dfs(self, needle):
        """ Performs a depth-first search for the given needle. """
        if self.value == needle:
            return self
        
        for node in self.children:
            result = node.search_dfs(needle)
            if result:
                return result
        
        return False

    def search_bfs(self, needle):
        """ Performs a breadth-first search for the given needle. """
        queue = list(self)

        while len(queue) > 0:
            current = queue.pop(0)
            if current.value == needle:
                return current
            else:
                queue.extend(self.children)

        return False

    def path_to(self, target):
        """
        Finds a path between the node self and the node target.
        """

        ## Get the list of nodes from self to root and from target to root.
        root = self.root
        self_to_root = root.__make_path(root, self)
        target_to_root = root.__make_path(root, target)

        ## Then go up the list self_to_root, adding nodes to path, 
        ## until a node which is an ancestor of both self and target 
        ## (i.e., is in the list target_to_root) is found.  From there, go
        ## down the list target_to_root.
        path = []
        current = self_to_root.pop(0)
        while current not in target_to_root:
            path.append(current)
            current = self_to_root.pop(0)

        target_to_current = target_to_root[0:target_to_root.index(current)]
        target_to_current.reverse()
        path.extend(target_to_current)
        return path

    def path(root, source, target):
        """
        Finds a path from the value source to the value target in the tree 
        which has the root node root.
        """
        source_node = root.search(source)
        target_node = root.search(target)
        if source_node and target_node:
            return source_node.path_to(target_node)
        else:
            raise KeyError

    def __make_path(self, root, target):
        """
        Takes two nodes, a "root" node and a target node which is a descendant 
        of root, and returns the list of nodes from target to root.
        """
        path = []
        while target != root:
            path.append(target)
            target = target.parent
        path.append(root)
        return path


def from_dlv(filename):
    """
    Function to build a taxonomy from the specified DLV output file.
    """
    # build regex for instance and link search
    regex_class = re.compile("class\(i(\d+)\)")
    regex_ins = re.compile("[ins|isa]\(i(\d+),i(\d+)\)")
    regex_links = re.compile("link\(i(\d+),i(\d+)\)")

    # process DLV output file
    with open(filename) as f:
        dlv = f.read()

        classes = frozenset(regex_class.findall(dlv))
        instances = frozenset(regex_ins.findall(dlv))
        links = frozenset(regex_links.findall(dlv))

    # set up taxonomy structure
    nodes = defaultdict(Node)
    root = Node("Philosophy", spine=True)

    # populate instances
    for child, parent in instances:
        nodes[parent].graft(nodes[child])

    # populate links
    for target, source in links:
        nodes[source].links.add(nodes[target])

    # glue taxonomies together, initialize values
    for key,node in nodes.iteritems():
        node.value = key

        # specify hand-built portion of the taxonomy
        if node.value in classes:
            node.spine = True

        # if this is a root, glue it to the Philosophy node.
        if node.parent is None:
            root.graft(node)

    return root
