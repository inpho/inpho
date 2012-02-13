# takes an ordered collection of lists and merges any redundancies, privileging from left to right
def list_merge(*lists):
    if not lists:
        raise ValueError("list_merge is undefined for zero arguments")
    
    new_lists = [lists[0]]
    for i, ls1 in enumerate(lists[1:]):
        s1 = set(ls1)
        # indexes to i+1 since the parent loop enumerates from index 1
        for ls2 in lists[:i+1]:
            s2 = set(ls2)
            s1.difference_update(s2)
        new_lists.append(list(s1))
    return new_lists
