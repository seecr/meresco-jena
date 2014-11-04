## begin license ##
#
# The Meresco Jena package is an Jena Fuseki Triplestore
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Jena"
#
# "Meresco Jena" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Jena" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Jena"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from urllib import urlencode
from meresco.triplestore import HttpClient as TriplestoreHttpClient

class HttpClient(TriplestoreHttpClient):

    def __init__(self, pathPrefix='/ds', **kwargs):
        super(HttpClient, self).__init__(pathPrefix=pathPrefix, **kwargs)

    def add(self, identifier, data, **kwargs):
        yield self._httpRequest(path='{0}/data'.format(self._dataset), arguments={'graph': identifier}, data=data, method='PUT')

    def delete(self, identifier, **kwargs):
        yield self._httpRequest(path='{0}/data'.format(self._dataset), arguments={'graph': identifier}, method='DELETE')

    def executeQuery(self, query, queryResultFormat='application/sparql-results+json'):
        result = yield super(HttpClient, self).executeQuery(query=query, queryResultFormat=queryResultFormat)
        raise StopIteration(result)

    def _httpRequest(self, path, arguments, method, data=None):
        path = "{0}/data?{1}".format(self._dataset, urlencode(arguments))
        headers = {}
        if data:
            headers={'Content-Type': 'application/rdf+xml', 'Content-Length': len(data)}
        if self.synchronous:
            host, port = self._triplestoreServer()
            header, body = self._urlopen('http://{0}:{1}{2}'.format(host, port, path), data=data, method=method, headers=headers)
        else:
            response = yield self._httppost(host=host, port=port, request=path, body=body, headers=headers)
            header, responseBody = response.split("\r\n\r\n", 1)
            self._verify20x(header, response)
        raise StopIteration((header, body))
