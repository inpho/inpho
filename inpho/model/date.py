month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May',
              6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 
              11:'November', 12:'December'}

class Date(object):
    """ SQLAlchemy wrapper for Date objects """

    def __init__(self, entity_id, relation_id, year=None, month=None, day=None, year_end=None, month_end=None, day_end=None):
        self.entity_id = entity_id
        self.relation_id = relation_id
        self.year = year
        self.month = month
        self.day = day
        self.year_end = year_end
        self.month_end = month_end
        self.day_end = day_end

    def __str__(self):
        '''
        Pretty prints a date.
        '''
        string = ""
        string += Date._print_date(self.year, self.month, self.day)

        if self.year_end:
            string += ' - '
            string += Date.print_date(self.year_end, self.month_end, self.day_end)

        return string

    def __eq__(self, other):
        return (self.entity_id == other.entity_id and 
                self.relation_id == other.relation_id and
                self.year == other.year and 
                self.month == other.month and
                self.day == other.day and
                self.year_end == other.year_end and
                self.month_end == other.month_end and
                self.day_end == other.day_end)

    @staticmethod
    def _print_date(year, month, day):
        string = ''
        if month:
            string += month_dict[month] + " "
            if day:
                string += str(day) + ", "

        string += str(abs(year))
        if year < 0:
            string += " B.C.E."
        return string

    def __repr__(self):
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
        def parse_date(iso_string):
            bce = (iso_string[0] == '-')

            if bce:
                iso_string = iso_string[1:]

            if len(iso_string) == 8:
                date = [int(iso_string[0:4]), int(iso_string[4:6]), int(iso_string[6:8])]
            elif len(iso_string) == 6:
                date = [int(iso_string[0:4]), int(iso_string[4:6]), 0]
            elif len(iso_string) == 4:
                date = [int(iso_string[0:4]), 0, 0]
            else:
                raise Exception("Invalid date string")
            
            if bce:
                date[0] *= -1
            else:
                date[0] += 1

            return date

        if '/' in iso_string:
            begin, end = iso_string.split('/')
            begin = parse_date(begin)
            end = parse_date(end)
        else:
            begin = parse_date(iso_string)
            end = [None, None, None]

        year, month, day = begin
        year_end, month_end, day_end = end

        date = Date(entity_id, relation_id, year, month, day, year_end, month_end, day_end)

        return date
