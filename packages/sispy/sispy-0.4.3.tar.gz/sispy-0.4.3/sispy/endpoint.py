# -*- coding: utf-8 -*-

import logging

from . import Error, Response, http, json, NullHandler

LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())

class Endpoint(object):

    """SIS endpoint"""

    def __init__(self, endpoint, client):
        self.endpoint = endpoint
        self.client = client

    def fetch_page(self, query=None):
        """Returns a Response() list-like object

        Response()._meta.total_count is the total number of items

        """
        return self._get(query=query)

    def fetch_all(self, query=None):
        """Calls fetch_page() multiple times to retrieve all items,
        returns a Response() list-like object of items fetched.

        Response._meta.headers is set to headers of the last HTTP request

        """    
        if not query:
            query = {}

        results = []
        while True:
            response = self.fetch_page(query)
            results.extend(list(response))
            if len(results) >= response._meta.total_count:
                break
            query['offset'] = len(results)

        response._result = results
        return response

    def get(self, id):
        """API GET """
        return self._get(id)

    def create(self, content):
        """API POST """

        headers = self._get_headers(add_content=True)
        request = http.Request(uri=self._get_uri(),
                               method='POST',
                               body=json.dumps(content),
                               headers=headers)

        return self.client.request(request)

    def update(self, id, content, query=None):
        """API PUT """

        headers = self._get_headers(add_content=True)
        request = http.Request(uri=self._get_uri(id, query),
                               method='PUT',
                               body=json.dumps(content),
                               headers=headers)

        return self.client.request(request)

    def delete_bulk(self, query):
        """Bulk delete.

        Returns: a Response dict-like object in the form of
        {
            'errors': [<items>],
            'success': [<items>]
        }

        """
        if not isinstance(query, dict) \
            or not isinstance(query.get('q', None), dict):
            err_msg = 'query must be a dictionary and contain a "q" dict'
            raise Error(http_status_code=400,
                        error=err_msg,
                        code=0,
                        response_dict={ })

        q = query.get('q')
        if not len(list(q.keys())):
            err_msg = 'query dictionary must not be empty' 
            raise Error(http_status_code=400,
                        error=err_msg,
                        code=0,
                        response_dict={ })

        headers = self._get_headers(add_content=True)
        request = http.Request(uri=self._get_uri(query=query),
                               method='DELETE',
                               headers=headers)

        return self.client.request(request)

    def delete(self, id):
        """API DELETE"""

        headers = self._get_headers(add_content=True)
        request = http.Request(uri=self._get_uri(id),
                               method='DELETE',
                               headers=headers)

        return self.client.request(request)

    def _get(self, obj=None, query=None):
        headers = self._get_headers(add_content=True)
        request = http.Request(uri = self._get_uri(obj, query),
                               headers=headers)
        
        return self.client.request(request)

    def _get_headers(self, add_content):
        headers = {
            'Accept': 'application/json'
        }

        if add_content:
            headers['Content-Type'] = 'application/json'

        if self.client.auth_token:
            headers['x-auth-token'] = self.client.auth_token

        return headers

    def _get_uri(self, obj=None, query=None):
        query_str = ''
        path_str = ''

        # ignore empty dict
        if isinstance(query, dict) and query:
            query = query.copy()
            for k in query:
                # support cas / q params as dict
                if isinstance(query[k], dict):
                    query[k] = json.dumps(query[k])

            query_str = '?{0}'.format(http.urlencode(query))

        if obj:
            path_str = '/{0}'.format(str(obj))

        resp = '{0}/{1}{2}{3}'.format(self.client.base_uri, self.endpoint,
                                  path_str, query_str)
        return resp

