__author__ = 'rbr'

import urllib
import urllib2
from xml.dom import minidom
import json

host = 'http://www.aquamonitor.no/'
#host = 'http://localhost/'
#host = 'http://151.157.129.195/'


class RequestWithMethod(urllib2.Request):
   def __init__(self, method, *args, **kwargs):
    self._method = method
    urllib2.Request.__init__(self, *args, **kwargs)

   def get_method(self):
    return self._method


def requestService(url, params):

    req = urllib2.Request(url, urllib.urlencode(params))
    response = urllib2.urlopen(req)

    return minidom.parseString(response.read())


def login(site, username, password):

    loginurl =  host + site + '/WebServices/LoginService.asmx/AuthenticateUser'
    loginparams = {'username':username, 'password':password}

    userdom = requestService(loginurl, loginparams)

    usertype = userdom.getElementsByTagName('Usertype')[0].childNodes[0].nodeValue

    if not usertype == 'NoUser':
        token = userdom.getElementsByTagName('Token')[0].childNodes[0].nodeValue
    else:
        token = None

    return token


def getJson(token, path):
    header = {'Cookie':'aqua_key='+token+';'}
    req = urllib2.Request(host + path, None, header)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def postJson(token, path, inJson):

    header = {'Content-Type':'application/json','Cookie':'aqua_key='+token+';'}
    req = urllib2.Request(host+path, json.dumps(inJson), header)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def putJson(token, path, inJson):

    header = {'Content-Type':'application/json','Cookie':'aqua_key='+token+';'}
    opener = urllib2.build_opener(urllib2.HTTPHandler)

    req = urllib2.Request(host+path, json.dumps(inJson), header)
    req.get_method = lambda: "PUT"
    response = opener.open(req)
    return json.loads(response.read())


def getProject(token, projectId):

    projectsurl = 'AquaServices/api/projects/'+ str(projectId)
    return getJson(token, projectsurl)

def getStations(token, projectId):

    stationsurl = 'AquaServices/api/projects/' + str(projectId) + '/stations/'
    return getJson(token, stationsurl)

def getArchive(token, id):
    header = {'Content-Type': 'application/json', 'Cookie':'aqua_key='+token+';'}
    archiveurl = host + 'AquaServices/files/archive/' + id
    #print(token, id)
    req = urllib2.Request(archiveurl, None, headers=header)
    response = urllib2.urlopen(req)
    return json.loads(response.read())


def createDatafile(token, data):

    header = {'Content-Type': 'application/json', 'Cookie':'aqua_key='+token+';'}
    datafileurl = host + 'AquaServices/files/datafile/'
    req = urllib2.Request(datafileurl, json.dumps(data), header)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def deleteArchive(token, id):
    header = {'Content-Type': 'application/json', 'Cookie':'aqua_key='+token+';'}
    opener = urllib2.build_opener(urllib2.HTTPHandler)

    archiveurl = host + 'AquaServices/files/archive/' + id
    req = urllib2.Request(archiveurl, None, headers=header)
    req.get_method = lambda: "DELETE"
    response = opener.open(req)

    return response.read()

def download(token, id, file, path):
    output = open(path, 'wb')

    url = host + "AquaServices/files/archive/" + id + '/' + file

    headers = {'Cookie' : 'aqua_key=' + token + ';'}

    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req)
    output.write(resp.read())
    output.close()