#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

from __future__ import unicode_literals
import urllib2
import cookielib
import json
import poster
import os


host = "https://api.github.com"
httpdebuglevel = 0
handlers = [
    poster.streaminghttp.StreamingHTTPSHandler(
        debuglevel=httpdebuglevel),
    urllib2.HTTPSHandler(debuglevel=httpdebuglevel),
    urllib2.HTTPHandler(debuglevel=httpdebuglevel),
    poster.streaminghttp.StreamingHTTPHandler(
        debuglevel=httpdebuglevel),
    poster.streaminghttp.StreamingHTTPRedirectHandler(),
    urllib2.HTTPCookieProcessor(cookielib.CookieJar())]
urllib2.install_opener(urllib2.build_opener(*handlers))


def glist():
    url = "/".join([host, "orgs", "linagora", "repos"])
    url += "?type=all"
    print "list url : " + url
    # Building request
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    request.add_header('Accept', 'application/json')
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for list : ", code
    return resultq.read()


def glist2():
    url = "/".join([host, "repos", "linagora", "linshare-core", "issues"])
    url += "?state=all"
    print "list url : " + url
    # Building request
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    request.add_header('Accept', 'application/json')
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for list : ", code
    return resultq.read()



#############################################################
# MAIN 
#############################################################

data = glist()
json_obj = json.loads(data)
# debug
# print json.dumps(json_obj, sort_keys=True, indent=2)
# print json_obj[0]
print "row count : ", len(json_obj)
for repo in json_obj:
    full_name = repo.get('full_name')
    #print full_name
    if full_name.startswith("linagora/linshare"):
        print "----------------"
        print repo.get('id')
        print repo.get('name')
        print repo.get('full_name')
        print "----------------"

data = glist2()
json_obj = json.loads(data)
# print len(json_obj)
print json.dumps(json_obj, sort_keys=True, indent=2)

pull_request = 0
pull_request_closed = 0
issue_closed = 0
for issue in json_obj:
    if issue.get("pull_request", False):
        pull_request += 1
        if issue.get("state") == "closed":
            pull_request_closed += 1
    else:
        if issue.get("state") == "closed":
            issue_closed += 1

print pull_request
print pull_request_closed
print issue_closed
print len(json_obj) - pull_request
print 
