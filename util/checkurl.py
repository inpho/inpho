import urllib
import time
import sys
from inpho.model import Session, Journal

if __name__ == "__main__":
    # must load in inpho environment - SQL Session, model, etc.

    # Get a list of all of the journals in the database and then, for each
    # journal in the list, make a request to the URL stored in the database
    # to see if it is still valid.  If the status code is a 302 redirect, 
    # update the URL in the database.  If it's accessible (status code == 
    # 200 or 30x), update the last_accessed field.  If it doesn't open at all, 
    # raise an error.  If it's been inaccessible for four weeks, raise an 
    # error.

    journal_list = Session.query(Journal).all()
    for journal in journal_list:
        valid = journal.check_url()
        if not valid:
            errormsg = "As of {0}, the journal {1} had a bad URL: {2}"
            print >> sys.stderr, errormsg.format(time.strftime("%Y-%m-%d %H:%M:%S"), journal.name, journal.URL)

        # "magic number" 2419200 == four weeks in seconds
        if not journal.last_accessed or (time.time() - journal.last_accessed > 2419200):
            errormsg = "As of {0}, the journal {1} has been inaccessible for four weeks."
            print >> sys.stderr, errormsg.format(time.strftime("%Y-%m-%d %H:%M:%S"), journal.name)

        Session.commit()
        Session.flush()

    print "Succesfully checked {0} journal URLS.".format(len(journal_list))
