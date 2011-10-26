from inpho.model import *

def generate_input():
    """
    Prints the DLV input to STDOUT
    """
    # Set of terms which appear
    appearances = set()
    appearances.update(print_taxonomy())
    appearances.update(print_evaluations(IdeaEvaluation))
    appearances.update(print_evaluations(AnonIdeaEvaluation))
    print_appearances(appearances)

def print_taxonomy():
    """
    Prints DLV input for the taxonomy, covering the class and isa atoms.
    Returns the list of terms which occur in the database.
    """
    # Set of terms which appear
    appearances = set()
    
    # Select concept_id and parent_concept_id pairs
    ids = Session.query(Node.concept_id, Node.parent_concept_id).all()

    # Build up atoms for hand-built taxonomy
    for concept_id, parent_concept_id in ids:
        appearances.update([concept_id, parent_concept_id])
    
        print "class(i%s)." % (concept_id)
        if parent_concept_id:
            print "isa(i%s, i%s)." % (concept_id, parent_concept_id)

    return appearances

def print_evaluations(type=IdeaEvaluation):
    """
    Prints DLV atoms for evaluations, covering the p#, mg, ms, sg, and ic.
    Returns the list of terms which occur in the database.
    """
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

def print_appearances(appearances):
    """
    Prints DLV atoms for appearances, covering the i atom.
    Returns the same as the input variable.
    """
    for idea in appearances:
        print "i(i%s)." % idea

    return appearances

if __name__ == '__main__':
    generate_input()
