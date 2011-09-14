"""
Library for performing fuzzymatches and search pattern construction.

When a new SEP article is published, an attempt is made to match article titles
with a pre-existing InPhO Entity for use with the data mining. To do this we use
fuzzymatching to search for variations in spellings.

We also have processing functions for handling search strings with union and
intersection clauses, covering such broad searches as 'philosophies of the
particular sciences'.

The methods in this file could use significant attention, as they are mostly
extracted from their context in a legacy interface.
"""
from inpho.lib.php import PHP
from inpho.model import Session
from inpho.model import Entity
from inpho import config

def fuzzymatch(string1, string2):
    """
    Takes two strings and performs a fuzzymatch on them. 
    Returns a (confidence, distance) tuple.
    """
    php = PHP("""set_include_path('%(lib_path)s'); 
                 require 'fuzzymatch.php';""" % 
                 {'lib_path': config.get('general', 'lib_path')})


    code = '$string1 = utf8_decode("' + string1.encode('utf8') + '");'
    code += '$string2 = utf8_decode("' + string2.encode('utf8') + '");'
    code += 'print fuzzy_match($string1, $string2, 2);'

    result = php.get_raw(code)
    confidence,distance = map(float, result.split(','))

    return (confidence, distance)

def fuzzymatch_all(string1):
    """
    Takes a string and returns all potential fuzzymatches from the Entity
    database. Matches are returned as a list of (entity,confidence) tuples.
    """
    # construct Entity query  
    entities = Session.query(Entity)
    entities = entities.filter(Entity.typeID != 2) # exclude nodes
    entities = entities.filter(Entity.typeID != 4) # exclude journals

    # initialize result object
    matches = []
   
    # build results
    for entity in entities:
        confidence, distance = fuzzymatch(string1, entity.label)
        if confidence >= 0.5:
            matches.append((entity,confidence))
    
    return matches

def convertSS(choicestring, ioru):
    #takes one of the output choices from setup_SSL(), as well as whether we are dealing with intersection or union
    #returns a pair of string--[searchstring, searchpattern]
    #where relevant, assume union by default (e.g. if ioru = anything other than 'i', union is implemented)
    #get first three characters of string to see which option from setup_SSL() we have
    #eventually replace choicestring in output with output from Jaimie's function
    split = choicestring.split(': ')

    #get # choice in "option" and string to be massaged in "string"
    sstring = split[1]
    option = split[0]

    ideas = sstring.split(' <and> ')

    #Options #1, 2  --do nothing, return sstring
    
    #3,4,5,6, 11:  idea1<and>idea2 ...<and>idean
    if option == '3' or option == '4' or option == '5' or option=='6' or option == '11':
        if ioru == 'i':
            sstring = "<i>".join(ideas)
            #spattern = "(( " + ideas[0] + "(
        else:
            sstring = "<u>".join(ideas)
    
    #7:  <idea1> and <idea2> and <area>
    #change to: 
    #(Idea1<i>area)<u>(idea2<i>area) or
    #(idea1<i>area)<i>(idea2<i>area)
    #8 <adj idea1> and <adj idea2> and <area>)
    #to (adj idea1<i>area)<u>(adj idea2<i>area)
    #(adj idea1<i>area)<i>(adj idea2<i>area)
    elif option == '7' or option == '8':
        ideaarea1 = '(' + "<i>".join([ideas[0], ideas[2]]) + ')'
        ideaarea2 = '(' + "<i>".join([ideas[1], ideas[2]]) + ')'
        if ioru == 'i':
            sstring = "<i>".join([ideaarea1, ideaarea2]) 
        else:
            sstring = "<u>".join([ideaarea1, ideaarea2])
    
    #Option 9: <idea> and <area1> and <area2> 
    #(idea<i>area1)<u>(idea<i>area2)
    #(idea<i>area1)<i>(idea<i>area2)
    elif option == '9':
        ideaarea1 = '(' + "<i>".join([ideas[0], ideas[1]]) + ')'
        ideaarea2 = '(' + "<i>".join([ideas[0], ideas[2]]) + ')'
        if ioru == 'i':
            sstring = "<i>".join([ideaarea1, ideaarea2]) 
        else: 
            sstring = "<u>".join([ideaarea1, ideaarea2])

    #<idea1> and <idea2> and <adj area1> and <adj area2>)
    #to(idea1<i>(area1<u>area2))<u>(idea2<i>(area1<u>area2))
    #(idea1<i>idea2)<i>(area1<u>area2)
    elif option == '10':
        areas = '(' + "<u>".join([ideas[2], ideas[3]]) + ')'
        jointideas = '(' + "<i>".join([ideas[0], ideas[1]]) + ')'
        ideaarea1 = '(' + "<i>".join([ideas[0], areas]) + ')'
        ideaarea2 = '(' + "<i>".join([ideas[1], areas]) + ')'
        if ioru == 'i':
            sstring = "<i>".join([jointideas, areas])
        else:
            sstring = "<u>".join([ideaarea1, ideaarea2])
            
    elif option == '11' or option == '12' or option == '13' or option == '14':
        if ioru == 'i':
            sstring = "<i>".join(ideas)
        else:
            sstring = "<u>".join(ideas)
    
    elif option == '15':
        if ioru == 'i':
            sstring = "<i>".join(ideas)
        else: 
            phil = ideas[:1]
            ideas = ideas[1:]
            sstring = phil[0] + "<i>(" + "<u>".join(ideas) + ")"

    return [sstring, choicestring]
