def titlecase(s):
    title = []
    for subst in s.split():
        title.append(subst[0].upper() + subst[1:])
    return ' '.join(title)
