#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

from __future__ import unicode_literals
import urllib2
import cookielib
import json
import poster
import os


host = "http://192.168.1.106:8080"
user = "bart.simpson@nodomain.com"
password = "secret"
base_url = "linshare/webservice/rest"
realm = "Name Of Your LinShare Realm"
httpdebuglevel = 0


auth_handler = urllib2.HTTPBasicAuthHandler()
# we convert unicode objects to utf8 strings because
# the authentication module does not handle unicode
auth_handler.add_password(
    realm=realm.encode('utf8'),
    uri=host.encode('utf8'),
    user=user.encode('utf8'),
    passwd=password.encode('utf8'))
handlers = [
    poster.streaminghttp.StreamingHTTPSHandler(
        debuglevel=httpdebuglevel),
    auth_handler,
    urllib2.HTTPSHandler(debuglevel=httpdebuglevel),
    urllib2.HTTPHandler(debuglevel=httpdebuglevel),
    poster.streaminghttp.StreamingHTTPHandler(
        debuglevel=httpdebuglevel),
    poster.streaminghttp.StreamingHTTPRedirectHandler(),
    urllib2.HTTPCookieProcessor(cookielib.CookieJar())]
# Setting handlers
# pylint: disable=W0142
urllib2.install_opener(urllib2.build_opener(*handlers))


def get_full_url(url_frament):
    root_url = host
    if root_url[-1] != "/":
        root_url += "/"
    root_url += base_url
    if root_url[-1] != "/":
        root_url += "/"
    root_url += url_frament
    return root_url


def lslist(url):
    """ List ressources store into LinShare."""
    url = get_full_url(url)
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


def lsdelete(url, data=None):
    """ List ressources store into LinShare."""
    url = get_full_url(url)
    print "delete url : " + url
    # Building request
    request = urllib2.Request(url)
    request.add_header('Accept', 'application/json')
    if data:
        # Building request
        post_data = json.dumps(data).encode("UTF-8")
        request = urllib2.Request(url, post_data)
        request.add_header('Accept', 'application/json')
        request.add_header('Content-Type',
                           'application/json; charset=UTF-8')
    request.get_method = lambda: 'DELETE'
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for delete : ", code
    return resultq.read()


def lscreate(url, data):
    """ List ressources store into LinShare."""
    url = get_full_url(url)
    print "create url : " + url
    # Building request
    post_data = json.dumps(data)
    post_data = post_data.encode("UTF-8")
    request = urllib2.Request(url, post_data)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    request.add_header('Accept', 'application/json')
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for create : ", code
    return resultq.read()


def lsupdate(url, data):
    """ List ressources store into LinShare."""
    url = get_full_url(url)
    print "update url : " + url
    # Building request
    post_data = json.dumps(data)
    post_data = post_data.encode("UTF-8")
    request = urllib2.Request(url, post_data)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    request.add_header('Accept', 'application/json')
    request.get_method = lambda: 'PUT'
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for update : ", code
    return resultq.read()


def upload(file_path, url, description=None):
    url = get_full_url(url)
    print "upload url : " + url
    print "file_path is : ", file_path
    file_name = os.path.basename(file_path)
    print "file_name is : ", file_name
    stream = file(file_path, 'rb')
    post = poster.encode.MultipartParam("file", filename=file_name, fileobj=stream)
    params = [post,]
    if description:
        params.append(("description", description))
    datagen, headers = poster.encode.multipart_encode(params)
    # Building request
    request = urllib2.Request(url, datagen, headers)
    request.add_header('Accept', 'application/json')
    # Do request
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for upload : ", code
    return resultq.read()

def extract_file_name(content_dispo):
    content_dispo = content_dispo.decode('unicode-escape').strip('"')
    file_name = ""
    for key_val in content_dispo.split(';'):
        param = key_val.strip().split('=')
        if param[0] == "filename":
            file_name = param[1].strip('"')
            break
    return file_name


def lsdownload(url):
    url = get_full_url(url)
    print "download url : " + url
    # Building request
    request = urllib2.Request(url)
    #request.add_header('Content-Type', 'application/json; charset=UTF-8')
    request.add_header('Accept', 'application/json;charset=UTF-8')
    # doRequest
    resultq = urllib2.urlopen(request)
    code = resultq.getcode()
    print "http code for download : ", code
    content_lenth = resultq.info().getheader('Content-Length')
    if not content_lenth:
        print "No content lengh header found !"
    content_dispo = resultq.info().getheader('Content-disposition')
    content_dispo = content_dispo.strip()
    file_name = extract_file_name(content_dispo)
    print "file_name is : ", file_name
    stream = file(file_name, 'w')
    chunk_size=256
    while 1:
        chunk = resultq.read(chunk_size)
        if not chunk:
            break
        stream.write(chunk)
    stream.flush()
    stream.close()



#############################################################
# MAIN 
#############################################################

data = lslist("documents")
json_obj = json.loads(data)
print "row count : ", len(json_obj)
# debug
# print json.dumps(json_obj, sort_keys=True, indent=2)
# print json_obj[0]

# lsdownload("documents/b141f17b-f45e-4ae6-b37c-e450f836d54b/download")

# exemple de post
#data = {
#    "prop1": "value1",
#    "prop1": "value1",
#}
#lscreate("url", data)

