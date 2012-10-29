import re
import os.path
import string
from urllib import quote_plus

import inpho.helpers

from sqlalchemy.ext.associationproxy import association_proxy
import inflect
p = inflect.engine()

class Searchpattern(object):
    def __init__(self, id, searchpattern):
        self.target_id = id
        self.searchpattern = searchpattern

def create_searchpattern(searchpattern):
    return Searchpattern(None, searchpattern)

class Entity(object):
    def url(self, filetype='html', action='view', id2=None):
        return inpho.helpers.url(controller="entity", id=self.ID, 
                                 action=action, id2=id2, filetype=filetype)

    def __repr__(self):
        return '<Entity %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label.encode('utf-8')

    def json_struct(self, sep_filter=True, limit=10, extended=True):
        """ Dictionary structure used with a :class:`JSONEncoder` """
        struct = { 'ID' : self.ID, 
                  'type' : 'entity',
                  'label' : self.label, 
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        return struct
    
    def json(self):
        """ Returns the object's utf8-encoded JSON representation """
        return ExtJsonEncoder(sort_keys=False, ensure_ascii=False, 
                              skipkeys=True).encode(self.json_struct())
    
    def web_search_string(self):
        # generates search string for search engines
        
        search_string = "\"" + self.label + "\""
        return search_string
    
    def get_filename(self, corpus_path=None):
        if corpus_path and self.sep_dir:
            filename = os.path.join(corpus_path, self.sep_dir,'index.html')
            if not os.path.exists(filename):
                filename = None
        else:
            filename = None

        return filename
    
    searchpatterns = association_proxy('_spatterns', 'searchpattern', creator=create_searchpattern)
    
    @property
    def patterns(self):
        newpatterns = ['\\b%s\\b' % pattern.replace(' * ', '( |.+ )') 
                            for pattern in self.searchpatterns]
        newpatterns.append('\\b%s\\b' % self.label)
        return newpatterns
        
    @property
    def google_url(self):
        google = "http://www.google.com/search?q="
        google += quote_plus(self.label.encode("utf-8"))
        return google 

    def pluralize(self):
        """
        Returns a list of all possible pluralizations

        >>> Session.query(Entity).get(2428)
        >>> entity.new_pluralize()
        ['philosophy of law', 'philosophy of laws', 'philosophies of law', 'philosophies of laws']
        """
        combinations = list()
        plurals = dict()

        words = self.label.split()

        # build up a dictionary of pluralizations to reuse - this way p.plural()
        # isn't being called multiple times per word.
        for word in words:
            wordtemp = word
            # process stoplist
            if word in ['in', 'of', 'or', 'and', 'for', 'on', 'about', 'to']:
                plurals[wordtemp] = [word]
            else:
                # singularize the words
                re.sub('ies$','y', word) or re.search('descartes$', word) or re.sub('ypes$', 'ype', word) or re.search('tus$', word) or re.sub('([ea])nges$', '\1nge', word) or re.sub('([aeiou])cles$', '\1cle', word) or re.sub('bles$', 'ble', word) or re.sub('ues$', 'ue', word) or re.sub('nces$', 'nce', word) or re.search('ous$', word) or re.search('sis$', word) or re.sub('xes$', 'x', word) or re.sub('([aeiou])(.)es$', '\1\2e', word) or re.sub('ces$', 'ce', word) or re.sub('es$', '', word) or re.search('ss$', word) or re.search('s$', '', word)
                plurals[wordtemp] = [word]
                plurals[wordtemp].append(p.plural(word))

        return inpho.helpers.make_combinations("", words, 0, plurals, combinations)
    
    def setup_SPL(self):
        #code to generate search pattern list to disambiguate ands to intersections or unions
        search_pattern_list = []
    
        #check to see whether label contains an and to be disambiguated
        if re.search(' and ', self.label):
            andsplit = self.label.split(' and ')
            search_pattern_list.append(andsplit[0] + '&cap' + andsplit[1])
            search_pattern_list.append(andsplit[0] + '&cup' + andsplit[1])
        
        search_pattern_list.append(self.label)
    
        return search_pattern_list
    
    def setup_SSL(self):
        exit = False
        search_string_list = []
        
        #Rewriting code to account for 8 options:
        #1. <idea>
        #2. <idea> [with 'in <area>' dropped]
        #3. <adj1> and <adj2> <idea>                    (= <adj1 idea> and <adj2 idea>)     
        #4. <idea1> and <idea2> 
        #5. <adj> <idea1> and <idea2>                  (= <adj idea1> and <adj idea2>)
        #6. 
        #7. <idea1> and <idea2> in <area>            (= <idea1> and <idea2> and <area>
        #8. <adj> <idea1> and <idea2> in <area>      (= <adj idea1> and <adj idea2> and <area>)
        #9. <idea> in <area1> and <area2>            (= <idea> and <area1> and <area2> )
        #10. <idea> in <adj> <area1> and <area2>      (= <idea> and <adj area1> and <adj area2>)
        #11. <phrase> <idea1>, <idea2>, and <idea3>   = <phrase idea1> and <phrase idea2> and <phrase idea3>
    
        #code for Option 1 (consult key above)
        #exact input is always a default option
        search_string_list.append('1: ' + self.label)
    
        #first split by "in", if applicable; I never need to combine processing of idea clause and area clause;
        #I can process them independently and then just tack on area clause at end as conjunction
        #note that there will always be something in insplit[0], not necessarily in insplit[1]
        
        #initialize strings and lists used in decision structures
        insplit = [None, None]
    
        ideaandsplit = [None, None]
        
        simpleand = None
        ideaandphrase = None
        
        option4 = None
    
        if re.search(' in ', self.label):
            insplit = self.label.split(' in ')
            #allow option to drop area if desired
            
            #Code for Option #2; allow dropping of "area" of desired or redundant
            search_string_list.append('2: ' + insplit[0])
            
        #now the idea phrase is in splitstring[0] and the area phrase is in splitstring[1]; I can process them identically
        #and just combine at the end
        #Code for Option 3 and Option 4
        
        if not insplit[0]:
            insplit[0] = self.label
    
        if re.search(' and ', insplit[0]):
            ideaandsplit = insplit[0].split(' and ')
            
            #convert string idea1, idea2 to list, to use pop
            idea1 = ideaandsplit[0].split(' ')
            idea2 = ideaandsplit[1].split(' ')
    
            #Option 3:  add simple conjunction to options
            simpleand = idea1 + ['<and>'] + idea2
            search_string_list.append('3: ' + " ".join(simpleand))
            
            #get adj phrase, if any, from idea1
            #add Option 4, distributing adjective, saving Option 4 in ideaandphrase to reuse in Option 6
            if len(idea1) > 1:
                noun = idea1.pop()
                adjphrase = idea1
                temp = adjphrase + idea2
                option4 = ideaandsplit[0].split(' ') + ['<and>'] + temp
                search_string_list.append('4: ' + " ".join(option4))
            elif len(idea2) > 1:
                noun = idea2.pop()
                adj1 = idea1
                adj2 = idea2
                option4 = adj1 + [noun] + ['<and>'] + adj2 + [noun]
                search_string_list.append('5: ' + " ".join(option4))
            
        areaphrase = None
        
        #process area phrase in the same way, if there is something in the second part of insplit and there is an 'and' in the area phrase
        #for Options 6-10
        if insplit[1] and re.search(' and ', insplit[1]):
            areaandsplit = insplit[1].split(' and ')
    
            #convert string area1, area2 to list, to use pop
            area1 = areaandsplit[0].split(' ')
            area2 = areaandsplit[1].split(' ')
            
            if len(area1) > 1:
                #print "we have a adj noun1 and noun2 situation"
                noun2 = area1.pop()
                adjphrase2 = area1
                temp = adjphrase2 + area2
                areaphrase = areaandsplit[0].split(' ') + ['<and>'] + temp
            elif len(area2) > 1:
                #print "we have a adj1 and adj2 noun situation"
                noun2 = area2.pop()
                adj1 = area1
                adj2 = area2
                areaphrase = adj1 + [noun2] + ['<and>'] + adj2 + [noun2]
                
            else:
                areaphrase = areaandsplit[0].split(' ')
            #now the completed area name is stored in list areaphrase
            #print "areaphrase is " 
            #print areaphrase
    
        #If there is an area, add option to naively add as conjunct; also add complex area phrase if applicable
        if insplit[1]:
            #Option 6; area but no and anywhere
            option6 = insplit[0] + ' <and> ' + insplit[1]
            search_string_list.append('6: ' + option6)
    
            #Option 7
            if simpleand:
                option7 = simpleand + ['<and>'] + insplit[1].split(' ')
                search_string_list.append('7: ' + " ".join(option7))
            
            #Option 8
            if option4:
                option8 = option4 + ['<and>'] + insplit[1].split(' ')
                search_string_list.append('8: ' + " ".join(option8))
            
            #Option 9
            if areaphrase:
                option9 = insplit[0].split(' ') + ['<and>'] + areaphrase
                search_string_list.append('9: '+ " ".join(option9))
            
            #Option 10
            if simpleand and areaphrase:
                option10 = simpleand + ['<and>'] + areaphrase
                search_string_list.append('10: ' + " ".join(option10))
            
        #print "label before re.search is " + self.label
        label = re.sub(" and", "", self.label)
        #split the idea up into components separated by and
        commasplit = label.split(',')
        
        #Option 11-14
        if re.search(',', self.label):
            #delete the extraneous and
            #print "it is triggering this"
            label = re.sub(" and", "", self.label)
            #split the idea up into components separated by and
            commasplit = label.split(',')
            
            #Option 11, simplest option:  just A and B and C
            search_string_list.append('11: ' + " <and>".join(commasplit))
            
            #Option 12, if an adj phrase is present, distribute
            if re.search(" ", commasplit[0]):
                adjphrase = commasplit[0].split(' ')
                joinedphrase1 = " ".join(adjphrase)
                noun1 = adjphrase.pop()
                commasplit = commasplit[1:]
                for noun in commasplit:
                    joinedphrase1 = joinedphrase1 + " <and> " + " ".join(adjphrase) + noun
                search_string_list.append('12: ' + joinedphrase1)
                
            
            #Option 14, if a prefix phrase is present at end, distribute inphrase to all
            commasplit = label.split(',')
            last = commasplit.pop()
            if re.search(" in ", last):
                lastnoun = last.split(' in ')
                inphrase = lastnoun.pop()
                commasplit.append(lastnoun.pop())
                joinedphrase2 = ""
                for noun in commasplit:
                    joinedphrase2 = joinedphrase2 + " <and>" + noun + " in " + inphrase
                joinedphrase2 = re.sub("^ <and>", "", joinedphrase2)
                search_string_list.append('13: ' + joinedphrase2)
                
                #Option 14 = both 12 and 13
                if re.search(" ", commasplit[0]):
                    joined1 = joinedphrase1.split(" <and> ")
                    joinedphrase3 = ""
                    for entry in joined1:
                        joinedphrase3 = joinedphrase3 + " <and> " + entry + " in " + inphrase
                    joinedphrase3 = re.sub("^ <and> ", "", joinedphrase3)
                    inphrase = " in " + inphrase + "$"
                    joinedphrase3 = re.sub(inphrase, "", joinedphrase3)
                    search_string_list.append('14: ' + joinedphrase3)
        
        #option 13:  thinker's (views on) X
        
        commasplit = label.split(',')
        #print "commasplit[0] is " + commasplit[0]
            
        if re.search('\'s* views on ', commasplit[0]) or re.search('\'', commasplit[0]):
            if re.search('\'s views on ', commasplit[0]):
                possesssplit = commasplit[0].split('\'s views on')
            elif re.search('\' views on ', commasplit[0]):
                possesssplit = commasplit[0].split('\' views on')
            elif re.search('\'s ', commasplit[0]):
                possesssplit = commasplit[0].split('\'s')
            elif re.search('\' ', commasplit[0]):
                possesssplit = commasplit[0].split('\'')
            else:
                exit = True
            if not exit:
                commasplit[0] = possesssplit[1]
                joinedphrase4 = possesssplit[0]
                for noun in commasplit:
                    joinedphrase4 = joinedphrase4 + " <and>" + noun
                search_string_list.append('15: '+ joinedphrase4)
                        

        return search_string_list

class Alias(object):
    pass
