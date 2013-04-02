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
def getVolumesFromDataAPI(token, volumeIDs, concat):
    data = None

    assert volumeIDs is not None, "volumeIDs is None"
    assert len(volumeIDs) > 0, "volumeIDs is less than one"
    
    url = dataapiEPR
    url = url + "volumes?volumeIDs=" + urllib.quote_plus('|'.join(volumeIDs))

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



def openZipStream(data):
    # create a zipfile from the data stream
    myzip = ZipFile(StringIO(data))

    #iterate over all items in the data stream
    for name in myzip.namelist():
        print "Zip Entry: ", name
        # print the file contents
        print myzip.read(name)


###   MAIN METHOD   ###
if __name__ == '__main__':
    username = config.get("hathitrust", "username")
    password = config.get("hathitrust", "password")
    
    volumeIDs  = ["uc2.ark:/13960/t2q52tn56",
                  "uc2.ark:/13960/t2q52xv16"]
    pageIDs    = ["uc2.ark:/13960/t2q52tn56[1,2,3,4,5]",
                  "uc2.ark:/13960/t2q52xv16[33,12,3,4,55]"]

    token = obtainOAuth2Token(username, password)

    if token is not None:
        print "obtained token: %s\n" % token
        ## to get volumes, uncomment next line
        data = getVolumesFromDataAPI(token, volumeIDs, False)

        ## to get pages, uncomment next line
        data = getPagesFromDataAPI(token, pageIDs, False)

        if data is not None:
            print openZipStream(data)
    else:
        print "Failed to obtain oauth token."

