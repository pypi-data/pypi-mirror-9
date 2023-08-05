# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# A number of different classes each fetching the same data from
# different sources (and with different data formats and data fidelity)
import os
import re
import functools
import codecs
from datetime import datetime, timedelta
from six.moves.urllib_parse import urljoin

from bs4 import BeautifulSoup
from rdflib import Literal
import requests
from six import text_type as str

from . import SwedishLegalSource, SwedishLegalStore, Trips, Regeringen, RPUBL
from ferenda import Describer
from ferenda import PDFDocumentRepository
from ferenda import CompositeRepository, CompositeStore
from ferenda import TextReader
from ferenda import util
from ferenda import PDFAnalyzer
from ferenda.decorators import managedparsing, downloadmax, recordlastdownload
from ferenda.elements import Paragraph
from ferenda.elements import Heading
from ferenda.elements import ListItem
from ferenda.errors import DocumentRemovedError


# custom style analyzer 
class DirAnalyzer(PDFAnalyzer):
    # direktiv has no footers
    footer_significance_threshold = 0
    def analyze_styles(self, frontmatter_styles, rest_styles):
        styledefs = {}
        all_styles = frontmatter_styles + rest_styles
        ds = all_styles.most_common(1)[0][0]
        styledefs['default'] = self.fontdict(ds)

        # title style: the 2nd largest style on the frontpage 
        if frontmatter_styles:
            ts = sorted(frontmatter_styles.keys(), key=self.fontsize_key, reverse=True)[1]
            styledefs['title'] = self.fontdict(ts)

        # h1 - h2: the two styles just larger than ds (normally set in the
        # same size but different weight)
        sortedstyles = sorted(rest_styles, key=self.fontsize_key)
        largestyles = [x for x in sortedstyles if
                       self.fontsize_key(x) > self.fontsize_key(ds)]
        for style in ('h2', 'h1'):
            if largestyles: # any left?
                styledefs[style] = self.fontdict(largestyles.pop(0))
        return styledefs

class Continuation(object):
    pass


class DirTrips(Trips):

    """Downloads Direktiv in plain text format from http://rkrattsbaser.gov.se/dir/"""
    alias = "dirtrips"
    app = "dir"
    base = "DIR"
    # start_url is created (by Trips.download_get_basefiles) from this:
    download_params = [{'maxpage': 101, 'app': app, 'base': base}]

    # overrides Trips.document_url_template
    document_url_template = "http://rkrattsbaser.gov.se/cgi-bin/thw?${APPL}=DIR&${BASE}=DIR&${HTML}=dir_dok&${TRIPSHOW}=format=THW&BET=%(basefile)s"

    rdf_type = RPUBL.Direktiv

    @recordlastdownload
    def download(self, basefile=None):
        if basefile:
            return super(DirTrips, self).download(basefile)
        else:
            if self.config.lastdownload and not self.config.refresh:
                startdate = self.config.lastdownload - timedelta(days=30)
                self.start_url += "&UDAT=%s+till+%s" % (
                    datetime.strftime(startdate, "%Y-%m-%d"),
                    datetime.strftime(datetime.now(), "%Y-%m-%d"))
            super(DirTrips, self).download()

    @managedparsing
    def parse(self, doc):
        # FIXME: need some way of telling intermediate_path that
        # suffix should be .txt (preferably w/o overriding
        # DocumentStore)
        intermediate_path = self.store.path(doc.basefile, 'intermediate', '.txt')
        downloaded_path = self.store.downloaded_path(doc.basefile)
        if not util.outfile_is_newer([downloaded_path], intermediate_path):
            html = codecs.open(downloaded_path, encoding="iso-8859-1").read()
            util.writefile(intermediate_path, util.extract_text(
                html, '<pre>', '</pre>'), encoding="utf-8")
        reader = TextReader(intermediate_path, encoding="utf-8")
        header_chunk = reader.readparagraph()
        self.make_meta(header_chunk, doc.meta, doc.uri, doc.basefile)
        self.make_body(reader, doc.body)

        # Iterate through body tree and find things to link to (See
        # EurlexTreaties.process_body for inspiration)
        self.process_body(doc.body, '', doc.uri)
        return doc

    def header_lines(self, header_chunk):
        n = util.normalize_space
        # This is a ridiculously complicated way of extracting
        # key-value headers when both keys and headers may be
        # continuated. The below, which relies on HTML tags enclosing
        # the value, is much simpler.
        # 
        # header = re.compile("([^:]+):\s*<b>([^<]*)</b>")
        # for m in header.finditer(header_chunk):
        #    yield [util.normalize_space(x) for x in m.groups()]
        ck = cv = ""
        for line in header_chunk.split("\n"):
            if ": " in line:
                # yield buffer
                if ck.strip() and cv.strip():
                    yield(n(ck), n(cv))
                    ck = ""
                k, cv = line.split(":", 1)
                if ck.strip():
                    ck += k
                else:
                    ck = k
            else:
                if line.startswith("    "):
                    cv += line
                else:
                    if ck.strip() and cv.strip():
                        yield(n(ck), n(cv))
                    ck = line
                    cv = ""
        yield(n(ck),n(cv))
                
    def make_meta(self, chunk, meta, uri, basefile):
        d = Describer(meta, uri)
        dcterms = self.ns['dcterms']
        prov = self.ns['prov']
        owl = self.ns['owl']
        rpubl = RPUBL

        d.rdftype(self.rdf_type)
        d.value(prov.wasGeneratedBy, self.qualified_class_name())

        # predicates maps key strings to corresponsing RDFLib terms,
        # e.g. "Rubrik" -> dcterms:title
        predicates = {'Dir nr': dcterms.identifier,
                      'Departement': rpubl.departement,
                      'Beslut vid regeringssammanträde':
                      rpubl.beslutsdatum,
                      'Rubrik': dcterms.title,
                      'Senast ändrad': dcterms.changed
                      }
        # munger contains a set of tuples where the first item is a
        # method for converting a plain text into the appropriate
        # RDFLib value, e.g:
        # - "Utredning av foo" => Literal("Utredning av foo",lang="sv")
        # - "1987-02-19" => datetime(1987,2,19)
        # - "Arbetsdepartementet" => URIRef("http://lagen.nu/terms/arbdep")
        # The second item is the Describer method that
        # should be used to add the value to the graph, i.e. .value
        # for Literals and .rel for URIRefs
        munger = {'Dir nr': (self.sanitize_identifier, d.value),  # the RDFLib constructor
                  'Departement': (functools.partial(self.lookup_resource, warn=False), d.rel),
                  'Beslut vid regeringssammanträde': (self.parse_iso_date, d.value),
                  'Rubrik': (self.sanitize_rubrik, d.value),
                  'Senast ändrad': (self.parse_iso_date, d.value)
                  }
        for (key, val) in self.header_lines(chunk):
            try:
                pred = predicates[key]
                (transformer, setter) = munger[key]
                setter(pred, transformer(val))
            except (KeyError, ValueError):
                self.log.error(
                    "Couldn't munge value '%s' into a proper object for predicate '%s'" % (val, key))

        d.rel(dcterms.publisher, self.lookup_resource("Regeringskansliet"))
        d.rel(owl.sameAs, self.sameas_uri(uri))
        self.infer_triples(d, basefile)
        # finally, we need a dcterms:issued, and the best we can come up
        # with is the "Beslut vid regeringssammanträde" date
        # (rpubl:beslutsdatum), so we copy it.
        d.value(dcterms.issued, d.getvalue(rpubl.beslutsdatum))

    def sanitize_rubrik(self, rubrik):
        if rubrik == "Utgår":
            raise DocumentRemovedError()

        rubrik = re.sub("^/r2/ ", "", rubrik)
        return Literal(rubrik, lang="sv")

    def sanitize_identifier(self, identifier):
        # "Dir.1994:111" -> "Dir. 1994:111"
        if re.match("Dir.\d+", identifier):
            identifier = "Dir. " + identifier[4:]
        if not identifier.startswith("Dir. "):
            identifier = "Dir. " + identifier
        return Literal(identifier)

    def make_body(self, reader, body):
        current_type = None
        for p in reader.getiterator(reader.readparagraph):
            new_type = self.guess_type(p, current_type)
            # if not new_type == None:
            #    print "Guessed %s for %r" % (new_type.__name__,p[:20])
            if new_type is None:
                pass
            elif new_type == Continuation and len(body) > 0:
                # Don't create a new text node, add this text to the last
                # text node created
                para = body.pop()
                para.append(p)
                body.append(para)
            else:
                if new_type == Continuation:
                    new_type = Paragraph
                body.append(new_type([p]))
                current_type = new_type

    def guess_type(self, p, current_type):
        if not p:  # empty string
            return None
        # complex heading detection heuristics: Starts with a capital
        # or a number, and doesn't end with a period (except in some
        # cases).
        elif ((re.match("^\d+", p)
               or p[0].lower() != p[0])
              and not (p.endswith(".") and
                       not (p.endswith("m.m.") or
                            p.endswith("m. m.") or
                            p.endswith("m.fl.") or
                            p.endswith("m. fl.")))):
            return Heading
        elif p.startswith("--"):
            return ListItem
        elif (p[0].upper() != p[0]):
            return Continuation  # magic value, used to glue together
                                 # paragraphs that have been
                                 # inadvertently divided.
        else:
            return Paragraph

    def process_body(self, element, prefix, baseuri):
        if isinstance(element, str):
            return
        fragment = prefix
        uri = baseuri
        for p in element:
            self.process_body(p, fragment, baseuri)

    def canonical_uri(self, basefile):
        return self.config.url + "res/dir/" + basefile

    @classmethod
    def tabs(cls, primary=False):
        return [['Förarbeten', '/forarb/']]


class DirAsp(SwedishLegalSource, PDFDocumentRepository):

    """Downloads Direktiv in PDF format from http://rkrattsdb.gov.se/kompdf/"""
    alias = "dirasp"
    start_url = "http://rkrattsdb.gov.se/kompdf/search.asp"
    document_url = "http://62.95.69.24/KOMdoc/%(yy)02d/%(yy)02d%(num)04d.PDF"
    source_encoding = "iso-8859-1"
    rdf_type = RPUBL.Direktiv

    def download(self):
        resp = requests.get(self.start_url)
        soup = BeautifulSoup(resp.text)
        depts = [opt['value'] for opt in soup.find_all("option", value=True)]
        for basefile, url in self.download_get_basefiles(depts):
            # since the server doesn't support conditional caching and
            # direktivs are basically never updated once published, we
            # avoid even calling download_single if we already have
            # the doc.
            if ((not self.config.refresh) and
                (not os.path.exists(self.store.downloaded_path(basefile)))):
                self.download_single(basefile, url)

    @downloadmax
    def download_get_basefiles(self, depts):
        for dept in depts:
            resp = requests.post(urljoin(self.start_url, 'sql_search_rsp.asp'),
                                 {'departement': dept.encode('latin-1'),
                                  'kom_nr': '',
                                  'title': '',
                                  'ACTION': '  SÖK  '.encode('latin-1')})
            soup = BeautifulSoup(resp.text)
            hits = list(soup.find_all(True, text=re.compile(r'(\d{4}:\d+)')))
            self.log.info("Searching for dept %s, %d results" % (dept, len(hits)))
            for hit in hits:
                link = hit.find_parent("a")
                # convert 2006:02 to 2006:2 for consistency
                segments = re.search("(\d+):(\d+)", link.text).groups()
                basefile = ":".join([str(int(x)) for x in segments])
                # we use link.absolute_url rather than relying on our
                # own basefile -> url code in remote_url. It seems
                # that in least one case the URL formatting rule is
                # not followed by the system...
                yield basefile, urljoin(self.start_url, link['href'])

    def remote_url(self, basefile):
        yy = int(basefile[2:4])
        num = int(basefile[5:])
        return self.document_url % {'yy': yy, 'num': num}

    def canonical_uri(self, basefile):
        return self.config.url + "res/dir/" + basefile

    def parse_from_pdfreader(self, pdfreader, doc):
        super(DirAsp, self).parse_from_pdfreader(pdfreader, doc)
        d = Describer(doc.meta, doc.uri)
        self.infer_triples(d, doc.basefile)
        return doc

    @classmethod
    def tabs(cls, primary=False):
        return [['Förarbeten', '/forarb/']]


class DirRegeringen(Regeringen):

    """Downloads Direktiv in PDF format from http://www.regeringen.se/"""
    alias = "dirregeringen"
    cssfiles = ['../ferenda/res/css/pdfview.css']
    jsfiles = ['../ferenda/res/js/pdfviewer.js']
    re_basefile_strict = re.compile(r'Dir\. (\d{4}:\d+)')
    re_basefile_lax = re.compile(r'(?:[Dd]ir\.?|) ?(\d{4}:\d+)')
    rdf_type = RPUBL.Direktiv
    document_type = Regeringen.KOMMITTEDIREKTIV
    sparql_annotations = None # don't even bother creating an annotation file

    def sanitize_identifier(self, identifier):
        # "Dir.1994:111" -> "Dir. 1994:111"
        if re.match("Dir.\d+", identifier):
            identifier = "Dir. " + identifier[4:]
        if not identifier.startswith("Dir. "):
            identifier = "Dir. " + identifier
        return Literal(identifier)

# inherit list_basefiles_for from CompositeStore, basefile_to_pathfrag
# from SwedishLegalStore)
class DirektivStore(CompositeStore, SwedishLegalStore):
    pass

        
# Does parsing, generating etc from base files:
class Direktiv(CompositeRepository, SwedishLegalSource):

    "A composite repository containing ``DirTrips``, ``DirAsp`` and ``DirRegeringen``."""
    subrepos = DirRegeringen, DirAsp, DirTrips
    alias = "dir"
    xslt_template = "res/xsl/forarbete.xsl"
    storage_policy = "dir"
    rdf_type = RPUBL.Direktiv
    documentstore_class = DirektivStore
    sparql_annotations = None # don't even bother creating an annotation file
    
    @classmethod
    def tabs(cls, primary=False):
        return [['Förarbeten', '/forarb/']]
