from unidecode import unidecode as udecode

def unidecode(text):
    """
    Takes a list of strings, applies unidecode to each string and
    returns the result. When unidecode returns [?], a blank space is
    output instead.
    """
    d = []
    for u in text:
        a = udecode(u)
        if a == '[?]':
            d.append(' ')
        else:
            d.append(a)
    return u''.join(d)
