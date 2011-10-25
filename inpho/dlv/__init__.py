from inpho.model import *

def generate_input():
    appearances = set()
    appearances.update(print_taxonomy())
    appearances.update(print_evaluations(IdeaEvaluation))
    appearances.update(print_evaluations(AnonIdeaEvaluation))
    print_appearances(appearances)

# Set of terms which appear
def print_taxonomy():
    appearances = set()
    ids = Session.query(Node.concept_id, Node.parent_concept_id).all()
    # Build up atoms for hand-built taxonomy
    for concept_id, parent_concept_id in ids:
        appearances.update([concept_id, parent_concept_id])
    
        print "class(i%s)." % (concept_id)
        if parent_concept_id:
            print "isa(i%s, i%s)." % (concept_id, parent_concept_id)

    return appearances

# Build up atoms for evaluations
def print_evaluations(type=IdeaEvaluation):
    appearances = set()

    evals = Session.query(type).limit(10).all()
    for eval in evals:
        appearances.update([eval.ante_id, eval.cons_id])
    
        # print the relatedness
        if eval.relatedness >= 0:
            print "p%s(i%s, i%s)." % (eval.relatedness, eval.ante_id, eval.cons_id)
    
        # Print the generality relation
        if eval.generality == 0:
            # more specific
            print "ms(i%s, i%s)." % (eval.ante_id, eval.cons_id)
        elif eval.generality == 1:
            # more general
            print "mg(i%s, i%s)." % (eval.ante_id, eval.cons_id)
        elif eval.generality == 2:
            # same generality
            print "sg(i%s, i%s)." % (eval.ante_id, eval.cons_id)
        elif eval.generality == 3:
            # inconsistent/incompatible
            print "ic(i%s, i%s)." % (eval.ante_id, eval.cons_id)

    return appearances

# Build up atoms for terms that appear
def print_appearances(appearances):
    for idea in appearances:
        print "i(i%s)." % idea

if __name__ == '__main__':
    generate_input()
