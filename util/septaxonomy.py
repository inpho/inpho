from inpho.model import Session, Node, Idea

def print_sep(node, depth=0):
    print "<li>"

    # Print SEP Link
    sep_dir = node.sep_dir if isinstance(node, Idea) else node.idea.sep_dir
    if sep_dir:
        print '<a href="http://plato.stanford.edu/entries/%s">%s</a>' % (sep_dir, node.label)
    else:
        print node.label

    # Print descendants
    descendants = list()
    if isinstance(node, Node):
        descendants.extend(node.children)
        descendants.extend(node.idea.instances)
    else:
        descendants.extend(node.instances)


    if descendants:
        print "<ul>"
        for idea in sorted(descendants, key=lambda x: x.label):
            print_sep(idea, depth+1)
        print "</ul>"
    
    print "</li>"

roots = Session.query(Node).filter(Node.parent_id==None).all()
print "<ul>"
for root in sorted(roots, key=lambda x: x.label):
    print_sep(root)
print "</ul>"


