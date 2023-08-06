# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import urllib2
import StringIO

from logilab.common.decorators import monkeypatch

from cubicweb.server.sources import datafeed
from cubicweb.xy import xy
from cubicweb.web.views import rdf


xy.register_prefix('dct', 'http://purl.org/dc/terms/')
xy.register_prefix('adms', 'http://www.w3.org/ns/adms#')
xy.register_prefix('dcat', 'http://www.w3.org/ns/dcat#')
xy.register_prefix('vcard', 'http://www.w3.org/2006/dcat/ns#')
xy.add_equivalence('Agent name', 'foaf:name')
xy.add_equivalence('Agent name', 'vcard:fn')  # XXX overrides ^?
xy.add_equivalence('Agent email', 'vcard:hasEmail')
xy.add_equivalence('Dataset identifier', 'dct:identifier')
xy.add_equivalence('Dataset title', 'dct:title')
xy.add_equivalence('Dataset creation_date', 'dct:issued')
xy.add_equivalence('Dataset modification_date', 'dct:modified')
xy.add_equivalence('Dataset description', 'dct:description')
xy.add_equivalence('Dataset keyword', 'dcat:keyword')
xy.add_equivalence('Dataset keyword', 'dcat:theme')
xy.add_equivalence('Dataset landing_page', 'dcat:landingPage')
xy.add_equivalence('Dataset frequency', 'dct:accrualPeriodicity')
xy.add_equivalence('Dataset spatial_coverage', 'dct:spatial')
xy.add_equivalence('Dataset provenance', 'dct:provenance')
xy.add_equivalence('Dataset dataset_distribution', 'dcat:distribution')
xy.add_equivalence('Dataset dataset_publisher', 'dct:publisher')
xy.add_equivalence('Dataset dataset_contact_point', 'adms:contactPoint')
xy.add_equivalence('Distribution access_url', 'dcat:accessURL')
xy.add_equivalence('Distribution description', 'dct:description')
xy.add_equivalence('Distribution format', 'dct:format')
xy.add_equivalence('Distribution licence', 'dct:license')


# "use-cwuri-as-url" option, only available from CubicWeb 3.20.
datafeed.DataFeedSource.options += (
        ('use-cwuri-as-url',
         {'type': 'yn',
          'default': None, # explicitly unset
          'help': ('Use cwuri (i.e. external URL) for link to the entity '
                   'instead of its local URL.'),
          'group': 'datafeed-source', 'level': 1,
          }),
        )

orig_update_config = datafeed.DataFeedSource.update_config
@monkeypatch(datafeed.DataFeedSource)
def update_config(self, source_entity, typed_config):
    orig_update_config(self, source_entity, typed_config)
    if typed_config['use-cwuri-as-url'] is not None:
        self.use_cwuri_as_url = typed_config['use-cwuri-as-url']
        self.public_config['use-cwuri-as-url'] = self.use_cwuri_as_url


# DataFeedParser.retrieve_url, only available from CubicWeb 3.20.
@monkeypatch(datafeed.DataFeedParser)
def retrieve_url(self, url, data=None, headers=None):
    """Return stream linked by the given url:
    * HTTP urls will be normalized (see :meth:`normalize_url`)
    * handle file:// URL
    * other will be considered as plain content, useful for testing purpose
    """
    headers = headers or {}
    if url.startswith('http'):
        url = self.normalize_url(url)
        if data:
            self.source.info('POST %s %s', url, data)
        else:
            self.source.info('GET %s', url)
        req = urllib2.Request(url, data, headers)
        return datafeed._OPENER.open(req, timeout=self.source.http_timeout)
    if url.startswith('file://'):
        return URLLibResponseAdapter(open(url[7:]), url)
    return URLLibResponseAdapter(StringIO.StringIO(url), url)


class URLLibResponseAdapter(object):
    """Thin wrapper to be used to fake a value returned by urllib2.urlopen"""
    def __init__(self, stream, url, code=200):
        self._stream = stream
        self._url = url
        self.code = code

    def read(self, *args):
        return self._stream.read(*args)

    def geturl(self):
        return self._url

    def getcode(self):
        return self.code

    def info(self):
        from mimetools import Message
        return Message(StringIO.StringIO())


# Monkeypatch RDF view (https://www.cubicweb.org/4745929).

@monkeypatch(rdf.RDFView)
def entity2graph(self, graph, entity):
    # aliases
    CW = rdf.CW
    urijoin = rdf.urijoin
    RDF = rdf.RDF
    URIRef = rdf.URIRef
    SKIP_RTYPES = rdf.SKIP_RTYPES
    Literal = rdf.Literal

    cwuri = URIRef(entity.cwuri)
    add = graph.add
    add( (cwuri, RDF.type, CW[entity.e_schema.type]) )
    try:
        for item in xy.xeq(entity.e_schema.type):
            add( (cwuri, RDF.type, urijoin(item)) )
    except xy.UnsupportedVocabulary:
        pass
    for rschema, eschemas, role in entity.e_schema.relation_definitions('relation'):
        rtype = rschema.type
        if rtype in SKIP_RTYPES or rtype.endswith('_permission'):
            continue
        for eschema in eschemas:
            if eschema.final:
                try:
                    value = entity.cw_attr_cache[rtype]
                except KeyError:
                    continue # assuming rtype is Bytes
                if value is not None:
                    add( (cwuri, CW[rtype], Literal(value)) )
                    try:
                        for item in xy.xeq('%s %s' % (entity.e_schema.type, rtype)):
                            add( (cwuri, urijoin(item[1]), Literal(value)) )
                    except xy.UnsupportedVocabulary:
                        pass
            else:
                for related in entity.related(rtype, role, entities=True, safe=True):
                    if role == 'subject':
                        add( (cwuri, CW[rtype], URIRef(related.cwuri)) )
                        try:
                            for item in xy.xeq('%s %s' % (entity.e_schema.type, rtype)):
                                add( (cwuri, urijoin(item[1]), URIRef(related.cwuri)) )
                        except xy.UnsupportedVocabulary:
                            pass
                    else:
                        add( (URIRef(related.cwuri), CW[rtype], cwuri) )

