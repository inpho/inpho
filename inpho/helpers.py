def titlecase(s):
    title = []
    for subst in s.split():
        title.append(subst[0].upper() + subst[1:])
    return ' '.join(title)

def url(controller, id=None, action=None, id2=None, filetype=None, **kwargs):
    if (id2 and (id == None or action == None)):
        raise ArgumentError()

    url = ''
    if controller:
        url += '/' + controller
    if id:
        url += '/' + str(id)
    if action:
        url += '/' + action
    if id2:
        url += '/' + str(id2)
    if filetype:
        url += '.' + filetype

    # construct the query string
    if kwargs:
        url += "?"
        for key in kwargs:
            if url[-1] != "?":
                url += "&"
            url += key + "=" + kwargs[key]

    return url

class ArgumentError(Exception):
    pass
