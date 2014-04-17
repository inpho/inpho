#!/usr/bin/env python

##
## hathiClient.py
##
## Author: Samuel Waggoner (samuel.waggoner@gmail.com)
##
## modelled after Yiming Sun's HathiClient.java
##

from array import array
import httplib ## used for making HTTP requests.
import json   ## used to process HTTP request responses.
import os.path
import urllib ## used to encode HTTP request queries.
from StringIO import StringIO ## used to stream http response into zipfile.
from zipfile import ZipFile  ## used to decompress requested zip archives.

from inpho import config

## Some Fields or something.
host = "silvermaple.pti.indiana.edu" # use over HTTPS
port = 25443
oauth2EPRurl = "/oauth2/token?grant_type=client_credentials"
dataapiEPR = "/data-api/"


## getVolumesFromDataAPI : String, String[], boolean ==> inputStream
def getVolumesFromDataAPI(token, volumeIDs, concat=False):
    data = None

    assert volumeIDs is not None, "volumeIDs is None"
    assert len(volumeIDs) > 0, "volumeIDs is less than one"
    
    url = dataapiEPR + "volumes"
    data = {'volumeIDs' : '|'.join(volumeIDs)}
    if concat:
        data['concat'] = 'true'

    print data['volumeIDs']
    return None

    headers = {"Authorization" : "Bearer " + token,
               "Content-type" : "application/x-www-form-urlencoded"}
    
    httpsConnection = httplib.HTTPSConnection(host, port)
    httpsConnection.request("POST", url, urllib.urlencode(data), headers)

    response = httpsConnection.getresponse()

    if response.status is 200:
        data = response.read()
    else:
        print "Unable to get volumes"
        print "Response Code: ", response.status
        print "Response: ", response.reason
        
    if httpsConnection is not None:
        httpsConnection.close()

    return data



def getPagesFromDataAPI(token, pageIDs, concat):
    data = None

    assert pageIDs is not None, "pageIDs is None"
    assert len(pageIDs) > 0, "pageIDs is less than one"
    
    url = dataapiEPR
    url = url + "pages?pageIDs=" + urllib.quote_plus('|'.join(pageIDs))

    if (concat):
        url = url + "&concat=true"

    print "data api URL: ", url

    httpsConnection = httplib.HTTPSConnection(host, port)

    headers = {"Authorization" : "Bearer " + token}
    httpsConnection.request("GET", url, headers=headers)

    response = httpsConnection.getresponse()

    if response.status is 200:
        data = response.read()
    else:
        print "Unable to get pages"
        print "Response Code: ", response.status
        print "Response: ", response.reason
        
    if httpsConnection is not None:
        httpsConnection.close()

    return data

    
def obtainOAuth2Token(username, password):
    token = None
    url = None
    httpsConnection = None
    
    httpsConnection = httplib.HTTPSConnection(host, port)

    url = oauth2EPRurl + "&client_secret=" + password
    url = url + "&client_id=" + username

    ## make sure to set the request content-type as application/x-www-form-urlencoded
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    ## make sure the request method is POST
    httpsConnection.request("POST", url, '', headers)

    response = httpsConnection.getresponse()

    ## if response status is OK
    if response.status is 200:
        data = response.read()

        jsonData = json.loads(data)
        print"*** JSON: ", jsonData
        
        token = jsonData["access_token"]
        print "*** parsed token: ", token
        

    else:
        print "Unable to get token"
        print "Response Code: ", response.status
        print "Response: ", response.reason

    if httpsConnection is not None:
        httpsConnection.close()
        
    return token



def printZipStream(data):
    # create a zipfile from the data stream
    with ZipFile(StringIO(data)) as myzip:

        #iterate over all items in the data stream
        for name in myzip.namelist():
            print "Zip Entry: ", name
            # print the file contents
            print myzip.read(name)


###   MAIN METHOD   ###
if __name__ == '__main__':
    from argparse import ArgumentParser
    import sys
    parser = ArgumentParser()
    parser.add_argument("-u", "--username", 
        help="HTRC username, default in inpho.config")
    parser.add_argument("-p", "--password", 
        help="HTRC password, default in inpho.config")
    parser.add_argument("-v", "--volumes", nargs='+', help="HTRC volume ids")
    parser.add_argument("--pages", nargs='+', help="HTRC page ids")
    parser.add_argument("--test", help="test with 2 volumes")
    parser.add_argument("file", nargs='?', help="input file of ids")
    parser.add_argument("-o", "--output", required=True, help="output directory")
    args = parser.parse_args()

    username = config.get("hathitrust", "username")
    password = config.get("hathitrust", "password")
   
    if args.test: 
        volumeIDs  = ["uc2.ark:/13960/t2q52tn56",
                      "uc2.ark:/13960/t2q52xv16"]
        pageIDs    = ["uc2.ark:/13960/t2q52tn56[1,2,3,4,5]",
                      "uc2.ark:/13960/t2q52xv16[33,12,3,4,55]"]
    elif args.file:
        with open(args.file) as IDfile:
            volumeIDs = [line.strip() for line in IDfile]
    else:
        volumeIDs = args.volumes
    
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    token = obtainOAuth2Token(username, password)
    if token is not None:
        print "obtained token: %s\n" % token
        ## to get volumes, uncomment next line
        data = getVolumesFromDataAPI(token, volumeIDs, False)

        ## to get pages, uncomment next line
        #data = getPagesFromDataAPI(token, pageIDs, False) 

        with ZipFile(StringIO(data)) as myzip:
            myzip.extractall(args.output)
    else:
        print "Failed to obtain oauth token."
        sys.exit(1)

