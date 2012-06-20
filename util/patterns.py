from inpho.model import *
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

patterns = Session.query(Searchpattern).all()

for pattern in Session.query(Searchpattern).all():
    pattern.searchpattern.replace('( | .+ )', ' * ')
    split_pattern = pattern.searchpattern.split(')|(')
    print pattern.target_id, split_pattern
    Session.delete(pattern)
    Session.commit()

    for p in split_pattern:
        p = p.replace('(', '').replace(')','').strip()
        if not Session.query(Searchpattern).get((pattern.target_id, p)):
            new_pattern = Searchpattern(pattern.target_id, p)
            Session.add(new_pattern)
            Session.commit()

