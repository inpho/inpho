from inpho.model import *

thinkers = Session.query(Thinker).all()

def migrate_dates(attr):
    if attr == 'birth':
        relation_id = 1
    elif attr == 'death':
        relation_id = 2

    for thinker in thinkers:
        year = getattr(thinker, attr+'_year')
        try:
            num_year = int(year)
        except:
            num_year = None
        month = getattr(thinker, attr+'_month')
        day = getattr(thinker, attr+'_day')

        # YEAR PROCESSING
        if num_year:
            year = str(num_year)
        elif year is not None and year.endswith('BC'):
            year = str(0 - int(year[0:(year.find('BC') - 1)]))
        elif year is not None and year.endswith('AD'):
            year = str(int(year[0:(year.find('AD') - 1)]))
        else:
            # if there is not a year, skip this thinker, move on
            continue

        # MONTH PROCESSING
        if month == 'January':
            month = 1
        elif month == 'February':
            month = 2
        elif month == 'March':
            month = 3
        elif month == 'April':
            month = 4
        elif month == 'May':
            month = 5
        elif month == 'June':
            month = 6
        elif month == 'July':
            month = 7
        elif month == 'August':
            month = 8
        elif month == 'September':
            month = 9
        elif month == 'October':
            month = 10
        elif month == 'November':
            month = 11
        elif month == 'December':
            month = 12
        else:
            month = None

        # DAY PROCESSING
        if day == '' or not int(day):
            day = None

        date = Date(thinker.ID, relation_id, year, month, day, None, None, None)
        Session.add(date)

migrate_dates('birth')
migrate_dates('death')

Session.commit()
                
