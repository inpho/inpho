class Date(object):
    """ SQLAlchemy wrapper for Date objects """

    def __init__(self, entity_id, relation_id, year=None, month=None, day=None, end_year=None, end_month=None, end_day=None):
        self.entity_id = entity_id
        self.relation_id = relation_id
        self.year = year
        self.month = month
        self.day = day
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
            
    def __str__(self):
        '''
        parses a date object into an iso_string                   
        '''
        begin_date_list = [self.year, self.month, self.day]
        end_date_list = [self.year_end, self.month_end, self.day_end]
        for i, date in enumerate(begin_date_list):
            if int(date[1]) == 0 or date is None:
                dates.pop(i)
        for i, date in enumerate(end_date_list):
            if int(date[1]) == 0 or date is None:
                dates.pop(i)
        if begin_date_list:
            begin_date = '-'.join(begin_date_list)
            if end_date_list:
                return '/'.join[begin_date, ('-'.join(begin_date_list))]
            else:
                return begin_date
        
    @staticmethod
    def convert_from_iso(entity_id, relation_id, iso_string):
        '''
        parses an iso_string into a date object                    
        '''
        date = None
        if '/' in iso_string:
            date_list = date_range.split('/')
            begin_date_string = date_list[0]
            end_date_string = date_list[1]
            begin_date_list = begin_date_string.split('-')
            end_date_list = end_date_string.split('-')
            year = begin_date_list[0] + 1
            month = begin_date_split[1]
            day = begin_date_split[2]
            year_end = end_date_split[0]
            month_end = end_date_split[1]
            day_end = end_date_split[2]
            date = Date(entity_id, relation_id, year, month, day, year_end, month_end, day_end)
        else:
            date_list = iso_string.split('-')
            year = date_list[0]
            month = date_list[1]
            day = date_list[2]
            date = Date(entity_id, relation_id, year, month, day, None, None, None)
                    
        Session.add(date)
        Session.commit()
