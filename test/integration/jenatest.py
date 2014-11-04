## begin license ##
#
# The Meresco Owlim package is an Owlim Triplestore based on meresco-triplestore
#
# Copyright (C) 2011-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Owlim"
#
# "Meresco Owlim" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Owlim" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Owlim"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from simplejson import loads

from weightless.core import compose, retval

from seecr.test.utils import getRequest, putRequest
from seecr.test.integrationtestcase import IntegrationTestCase

from meresco.jena import HttpClient
from meresco.triplestore import InvalidRdfXmlException, MalformedQueryException


class JenaTest(IntegrationTestCase):
    def testOne(self):
        header, body = getRequest(port=self.jenaPort, path='/ds/query', arguments=dict(query="SELECT ?s WHERE {}"), parse=False)
        self.assertTrue('<variable name="s"/>' in body, body)

    def testAddRdf(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description>
        <rdf:type>testAddRdf</rdf:type>
    </rdf:Description>
</rdf:RDF>"""
        putRequest(port=self.jenaPort, path="/ds/data?graph=uri:record",
                additionalHeaders={'Content-Type': 'application/rdf+xml', 'Content-length': len(rdf)},
                data=rdf, parse=False)
        header, body = getRequest(port=self.jenaPort, path='/ds/query', arguments=dict(query="SELECT ?o WHERE {?s ?p ?o}"), parse=False)
        self.assertTrue("<literal>testAddRdf</literal>" in body, body)

    def testAddRdfUsingClient(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description>
        <rdf:type>testAddRdfUsingClient</rdf:type>
    </rdf:Description>
</rdf:RDF>"""
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        list(compose(jenaClient.add('uri:identifier', rdf)))
        header, body = getRequest(port=self.jenaPort, path='/ds/query', arguments=dict(query="SELECT ?o WHERE {?s ?p ?o}"), parse=False)
        self.assertTrue("<literal>testAddRdfUsingClient</literal>" in body, body)

    def testQueryUsingClient(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description>
        <rdf:type>testQueryUsingClient</rdf:type>
    </rdf:Description>
</rdf:RDF>"""
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        list(compose(jenaClient.add('uri:identifier', rdf)))
        result = retval(jenaClient.executeQuery('select ?s where {?s ?p "testQueryUsingClient"}'))
        self.assertEquals(1, len(result))

    def testAddInvalidRdf(self):
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        try:
            list(compose(jenaClient.add('uri:identifier', '<invalidRdf/>')))
            self.fail("should not get here")
        except InvalidRdfXmlException, e:
            self.assertEquals('org.openrdf.rio.RDFParseException: Not a valid (absolute) URI: #invalidRdf [line 1, column 14]', str(e))

    def testAddInvalidIdentifier(self):
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        try:
            list(compose(jenaClient.add('identifier', '<ignore/>')))
            self.fail("should not get here")
        except ValueError, e:
            self.assertEquals('java.lang.IllegalArgumentException: Not a valid (absolute) URI: identifier', str(e))

    def testInvalidSparql(self):
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        try:
            list(compose(jenaClient.executeQuery("""select ?x""")))
            self.fail("should not get here")
        except MalformedQueryException, e:
            self.assertTrue(str(e).startswith('Error 400: Parse error:'), str(e))

    def testKillTripleStoreSavesState(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testKillTripleStoreSavesState</rdf:type>
        </rdf:Description>
    </rdf:RDF>"""
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        list(compose(jenaClient.add('uri:identifier', rdf)))

        json = self.query('SELECT ?x WHERE {?x ?y "uri:testKillTripleStoreSavesState"}')
        self.assertEquals(1, len(json['results']['bindings']))

        self.restartJenaServer()

        json = self.query('SELECT ?x WHERE {?x ?y "uri:testKillTripleStoreSavesState"}')
        self.assertEquals(1, len(json['results']['bindings']))

    def testDeleteRecord(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDelete</rdf:type>
        </rdf:Description>
    </rdf:RDF>"""
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        list(compose(jenaClient.add('uri:identifier', rdf)))

        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

        rdfUpdated = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDeleteUpdated</rdf:type>
        </rdf:Description>
    </rdf:RDF>"""
        list(compose(jenaClient.add('uri:identifier', rdfUpdated)))

        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(1, len(json['results']['bindings']))

        list(compose(jenaClient.delete('uri:identifier')))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(0, len(json['results']['bindings']))

        list(compose(jenaClient.add('uri:record', rdf)))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

    def testDescribeQuery(self):
        rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about="uri:test:describe">
            <rdf:value>DESCRIBE</rdf:value>
        </rdf:Description>
    </rdf:RDF>"""
        jenaClient = HttpClient(host='localhost', port=self.jenaPort, synchronous=True)
        list(compose(jenaClient.add('uri:identifier', rdf)))

        headers, body = getRequest(self.jenaPort, "/ds/query", arguments={'query': 'DESCRIBE <uri:test:describe>'}, additionalHeaders={"Accept" : "application/rdf+xml"}, parse=False)
        self.assertTrue("Content-Type: application/rdf+xml" in headers, headers)
        self.assertXmlEquals("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="uri:test:describe">
    <rdf:value>DESCRIBE</rdf:value>
</rdf:Description></rdf:RDF>""", body)

    def query(self, query):
        header, body = getRequest(port=self.jenaPort, path='/ds/query', arguments=dict(query=query), parse=False, additionalHeaders={'Accept': 'application/sparql-results+json'})
        return loads(body)

