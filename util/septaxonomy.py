from inpho.model import Session, Node, Idea

def print_sep(node, depth=0):
    print "<li>"
    sep_dir = node.sep_dir if isinstance(node, Idea) else node.idea.sep_dir

    if sep_dir:
        print '<a href="http://plato.stanford.edu/entries/%s">%s</a>' % (sep_dir, node.label)
    else:
        print node.label

    print "".join(["    "*depth, node.label]),
    if isinstance(node, Node):
        if node.idea.sep_dir:
            print "".join([" +", node.idea.sep_dir])
        else:
            print " "
        if node.children or node.idea.instances:
            print "<ul>"
            for idea in node.children:
                print_sep(idea, depth+1)
            for idea in node.idea.instances:
                print_sep(idea, depth+1)
            print "</ul>"
    else:
        if node.sep_dir:
            print "".join([" +", node.sep_dir])
        else:
            print " "

        if node.instances:
            print "<ul>"
            for idea in node.instances:
                print_sep(idea, depth+1)
            print "</ul>"
    print "</li>"

roots = Session.query(Node).filter(Node.parent_id==None).all()
print "<ul>"
for root in roots:
    print_sep(root)
print "</ul>"


