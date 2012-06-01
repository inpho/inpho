from inpho.model import *

patterns = Session.query(Searchpattern).all()

for pattern in patterns:
    search_patterns = str(pattern.searchpattern).split('|')
    
    for new_pattern in search_patterns:
        # remove any surrounding parens or whitespace
        new_pattern = new_pattern.strip('()').lstrip().rstrip()
        
        Session.add(new_pattern)
        Session.delete(pattern)
        Session.commit()
