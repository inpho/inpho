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
        date = [self.year, self.month, self.day, self.year_end, self.month_end, self.day_end]
        new_date = []
        for element in date:
            if element:
                if (element is self.year) or (element is self.year_end):
                    if element < 0:
                        if len(str(abs(element))) < 4:
                            new_date.append(str(element).zfill(5))
                        else:
                            new_date.append(str(element))
                    else:
                        if len(str(abs(element))) < 4:
                            new_date.append(str(element - 1).zfill(4))
                        else:
                            new_date.append(str(element - 1))
                elif (((element is self.month) or (element is self.month_end) or 
                       (element is self.day) or (element is self.day_end)) and 
                      (len(str(abs(element))) < 2)):
                    new_date.append(str(element).zfill(2))
                else:
                    new_date.append(str(element))
        new_date_length = len(new_date)
        if new_date_length > 3:
            return '/'.join([(''.join(new_date[0:3])), (''.join(new_date[3:new_date_length]))])
        else:
            return ''.join(new_date[0:new_date_length])
        
    @staticmethod
    def convert_from_iso(entity_id, relation_id, iso_string):
        '''
        parses an iso_string into a date object                    
        '''
        if iso_string:
            if '/' in iso_string:
                date_list = date_range.split('/')
                begin_date_string = date_list[0]
                end_date_string = date_list[1]
                begin_date_list = foo(begin_date_string)
                end_date_list = foo(end_date_string)
                year = begin_date_list[0]
                if year >= 0:
                    year += 1
                month = begin_date_list[1]
                day = begin_date_list[2]
                year_end = end_date_list[0]
                if year_end >= 0:
                    year_end += 1
                month_end = end_date_list[1]
                day_end = end_date_list[2]
                date = Date(entity_id, relation_id, year, month, day, year_end, month_end, day_end)
            else:
                date_list = foo(iso_string)
                year = date_list[0]
                if year_end >= 0:
                    year_end += 1
                month = date_list[1]
                day = date_list[2]
                date = Date(entity_id, relation_id, year, month, day, None, None, None)
        Session.add(date)
        Session.commit()
    
    @staticmethod
    def foo(iso_string):
        string_length = len(iso_string)
        if string_length > 4:
            if string_length == 8:
                return [int(iso_string[0:4]), int(iso_string[4:6]), int(iso_string[6:8])]
            else:    
                return [int(iso_string[0:4]), int(iso_string[4:6])]
        else:            
            return [int(iso_string[0:4])]
