# -*- coding: utf-8 -*-

import json
import logging

try:
    import httplib2
    HTTP_LIB = 'httplib2'
except ImportError:
    import urllib2
    HTTP_LIB = 'urllib2'

from . import Response, Error, Meta

LOG = logging.getLogger(__name__)

def get_handler(http_keep_alive=True):
    """ Returns an appropriate http handler object based on what's 
    http handling library is available

    """
    LOG.debug('using %s library to handle HTTP' % HTTP_LIB)

    if HTTP_LIB == 'urllib2':    
        return URLLIB2Handler()

    elif HTTP_LIB == 'httplib2':
        return HTTPLIB2Handler(http_keep_alive=http_keep_alive)

class Request(object):
    """ HTTP request proxy class

    """
    def __init__(self, uri, method='GET', body=None, headers=None):
        self.uri = uri
        self.method = method
        self.body = body
        self.headers = headers

    def __str__(self):
        s = ''
        s += '%s ' % self.method
        s += '%s ' % self.uri
        return s

class HTTPHandler(object):
    """ HTTP Handler proxy base class

    """
    def __init__(self, http_keep_alive=True):
        self.http_keep_alive = http_keep_alive

    def request(self):
        # child classes must overwrite this
        raise NotImplementedError()

class URLLIB2Handler(HTTPHandler):
    """ Handles http requests using urllib2 
    """
    def __init__(self, *args, **kwargs): 
        super(URLLIB2Handler, self).__init__(*args, **kwargs)

    def request(self, request):
        # create urllib2 Request() object, set uri and body contents if any
        new_req = urllib2.Request(request.uri, data=request.body)

        # add headers if present
        if request.headers:
            for header_name in request.headers:
                new_req.add_header(header_name, request.headers[header_name])

        # set method, if differet from GET
        if request.method != 'GET':
            # urllib2 method needs to be a callable method
            new_req.get_method = lambda: request.method

        # send request
        LOG.debug(request)
        try:
            response = urllib2.urlopen(new_req)
        except urllib2.HTTPError as e:
            response_dict = json.loads(e.read())
            code = response_dict.get('code')

            # attempt to use error from response body,
            # if not available use http error info
            error = response_dict.get('error')
            if not error:
                error = e.reason

            raise Error(http_status_code=e.code,
                        error=error,
                        code=code,
                        response_dict=response_dict)

        # read response
        result = json.loads(response.read())
        # build meta with headers as a dict
        meta = Meta(response.info().dict)
        # return Response object    
        return Response(result, meta)

class HTTPLIB2Handler(HTTPHandler):
    """ Handles HTTP requests using httplib2

    """          
    def __init__(self, *args, **kwargs):
        super(HTTPLIB2Handler, self).__init__(*args, **kwargs)

        self._http = httplib2.Http(disable_ssl_certificate_validation=True)
        
    def request(self, request):
        if not self.http_keep_alive:
            # ask the server to close the connection
            if not hasattr(request, 'headers'):
                request.headers = {}
            request.headers['Connection'] = 'close'

        LOG.debug(request)

        (response, content) = self._http.request(request.uri,
                                                 method=request.method,
                                                 body=request.body,
                                                 headers=request.headers)

        if not self.http_keep_alive:
            # manually force close any open connections
            for connection in self._http.connections.itervalues():
                if hasattr(connection, 'sock') and connection.sock:
                    connection.close()

        result = json.loads(content)
        meta = Meta(response)

        # raise Error if we got http status code >= 400
        if response.status >= 400:
            code = result.get('code')

            # attempt to use error from response body,
            # if not available set to None
            error = result.get('error')

            raise Error(http_status_code=response.status,
                        error=error,
                        code=code,
                        response_dict=result)

        # else return Response
        return Response(result, meta)

