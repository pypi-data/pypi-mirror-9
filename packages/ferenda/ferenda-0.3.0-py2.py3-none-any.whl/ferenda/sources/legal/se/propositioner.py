# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import os
from datetime import datetime
import codecs

from bs4 import BeautifulSoup
from lxml import etree
import requests
from layeredconfig import LayeredConfig
from six import text_type as str

from ferenda import util, errors
from ferenda.elements import UnicodeElement, CompoundElement, \
    Heading, Preformatted, Paragraph, Section, Link, ListItem, \
    serialize
from ferenda import CompositeRepository, CompositeStore
from ferenda import PDFDocumentRepository
from ferenda import Describer
from ferenda import TextReader
from ferenda import PDFReader
from ferenda import DocumentEntry
from ferenda.decorators import managedparsing
from . import Trips, NoMoreLinks
from . import Regeringen
from . import Riksdagen
from . import RPUBL
from . import SwedishLegalSource, SwedishLegalStore
from .swedishlegalsource import offtryck_parser, offtryck_gluefunc

class PropRegeringen(Regeringen):
    alias = "propregeringen"
    re_basefile_strict = re.compile(r'Prop. (\d{4}/\d{2,4}:\d+)')
    re_basefile_lax = re.compile(
        r'(?:Prop\.?|) ?(\d{4}/\d{2,4}:\d+)', re.IGNORECASE)
    rdf_type = RPUBL.Proposition
    document_type = Regeringen.PROPOSITION
    # sparql_annotations = "res/sparql/prop-annotations.rq"
    sparql_annotations = None # don't even bother creating an annotation file

class PropTrips(Trips):
    alias = "proptrips"
    base = "THWALLAPROP"
    app = "prop"

    basefile_regex = "(?P<basefile>\d+/\d+:\d+)$"
    download_params = [{'maxpage': 101, 'app': app, 'base': base}]

    downloaded_suffix = ".html"
    rdf_type = RPUBL.Proposition

    storage_policy = "dir"

    def get_default_options(self):
        opts = super(PropTrips, self).get_default_options()
        opts['lastbase'] = "THWALLAPROP"
        return opts

    # don't use @recordlastdownload -- download_get_basefiles_page
    # should set self.config.lastbase instead
    def download(self, basefile=None):
        if basefile:
            return super(PropTrips, self).download(basefile)
        else:
            if ('lastbase' in self.config and
                self.config.lastbase and
                not self.config.refresh):
                now = datetime.now()
                maxbase = "PROPARKIV%s%s" % (now.year % 100, (now.year+1) % 100)
                while self.config.lastbase != maxbase:
                    self.download_params[0]['base'] = self.config.lastbase  # override "THWALLAPROP" with eg "PROPARKIV0809"
                    r = super(PropTrips, self).download() # download_get_basefiles_page sets lastbase as it goes along
            else:
                r = super(PropTrips, self).download()
            LayeredConfig.write(self.config)      # assume we have data to write
            return r


    def _basefile_to_base(self, basefile):
        # 1992/93:23 -> "PROPARKIV9293"
        # 1999/2000:23 -> "PROPARKIV9900"
        (y1, y2, idx) = re.split("[:/]", basefile)
        return "PROPARKIV%02d%02d" % (int(y1) % 100, int(y2) % 100)

    def download_get_basefiles_page(self, pagetree):

        # feed the lxml tree into beautifulsoup by serializing it to a
        # string -- is there a better way?
        soup = BeautifulSoup(etree.tostring(pagetree))
        for tr in soup.findAll("tr"):
            if ((not tr.find("a")) or
                    not re.match(self.basefile_regex, tr.find("a").text)):
                # FIXME: Maybe re.search instead of .match to find
                # "Prop. 2012/13:152"
                continue
            # First, look at desc (third td):
            descnodes = [util.normalize_space(x) for x
                         in tr.find_all("td")[2]
                         if isinstance(x, str)]
            bilaga = None
            if len(descnodes) > 1:
                if descnodes[1].startswith("Bilaga:"):
                    bilaga = util.normalize_space(descnodes[0].split(",")[-1])
            desc = "\n".join(descnodes)

            # then, find basefile (second td)
            tds = tr.find_all("td")
            td = tds[1]
            basefile = td.a.text
            assert re.match(self.basefile_regex, basefile)

            basefile = self.sanitize_basefile(basefile)

            # assume entries are strictly sorted from ancient to
            # recent. Therefore, as soon as we encounter a new time
            # period (eg 1998/99) we can update self.config.lastbase
            self.config.lastbase = self._basefile_to_base(basefile)

            url = td.a['href']

            # self.download_single(basefile, refresh=refresh, url=url)

            # and, if present, extra files (in td 4+5)
            extraurls = []
            for td in tr.findAll("td")[3:]:
                extraurls.append(td.a['href'])

            # we slightly abuse the protocol between
            # download_get_basefiles and this generator -- instead of
            # yielding just two strings, we yield two tuples with some
            # extra information that download_single will need.

            yield (basefile, bilaga), (url, extraurls)

        nextpage = None
        for element, attribute, link, pos in pagetree.iterlinks():
            if element.text and element.text.strip() == "Fler poster":
                nextpage = link
        raise NoMoreLinks(nextpage)

    document_url_template = ("http://rkrattsbaser.gov.se/cgi-bin/thw?"
                             "${HTML}=prop_lst&${OOHTML}=prop_dok"
                             "&${SNHTML}=prop_err&${HILITE}=1&${MAXPAGE}=26"
                             "&${TRIPSHOW}=format=THW"
                             "&${SAVEHTML}=/prop/prop_form2.html"
                             "&${BASE}=%(base)s&${FREETEXT}=&${FREETEXT}="
                             "&PRUB=&DOK=p&PNR=%(pnr)s&ORG=")

    def remote_url(self, basefile):
        base = self._basefile_to_base(basefile)
        pnr = basefile.split(":")[1]
        return self.document_url_template % {'base': base,
                                             'pnr': pnr}
    

    def download_single(self, basefile, url=None):
        if url is None:
            url = self.remote_url(basefile)
            if not url:  # remote_url failed
                return
            
        # unpack the tuples we may recieve instead of plain strings
        mainattachment = None
        if isinstance(basefile, tuple):
            basefile, attachment = basefile
            if attachment:
                mainattachment = attachment + ".html"
        if isinstance(url, tuple):
            url, extraurls = url
        updated = created = False
        checked = True

        filename = self.store.downloaded_path(basefile, attachment=mainattachment)
        created = not os.path.exists(filename)

        # since the server doesn't support conditional caching and
        # propositioner are basically never updated once published, we
        # avoid even calling download_if_needed if we already have
        # the doc.
        if (os.path.exists(self.store.downloaded_path(basefile))
            and not self.config.refresh):
            self.log.debug("%s: already exists" % basefile)
            return
        
        if self.download_if_needed(url, basefile, filename=filename):
            if created:
                self.log.info("%s: downloaded from %s" % (basefile, url))
            else:
                self.log.info(
                    "%s: downloaded new version from %s" % (basefile, url))
            updated = True
        else:
            self.log.debug("%s: exists and is unchanged" % basefile)

        for url in extraurls:
            if url.endswith('msword.application'):
                # NOTE: We cannot be sure that this is
                # actually a Word (CDF) file. For older files
                # it might be a WordPerfect file (.wpd) or a
                # RDF file, for newer it might be a .docx. We
                # cannot be sure until we've downloaded it.
                # So we quickly read the first 4 bytes
                r = requests.get(url, stream=True)
                sig = r.raw.read(4)
                # r.raw.close()
                #bodyidx = head.index("\n\n")
                #sig = head[bodyidx:bodyidx+4]
                if sig == b'\xffWPC':
                    doctype = ".wpd"
                elif sig == b'\xd0\xcf\x11\xe0':
                    doctype = ".doc"
                elif sig == b'PK\x03\x04':
                    doctype = ".docx"
                elif sig == b'{\\rt':
                    doctype = ".rtf"
                else:
                    self.log.error(
                        "%s: Attached file has signature %r -- don't know what type this is" % (basefile, sig))
                    continue
            elif url.endswith('pdf.application'):
                doctype = ".pdf"
            else:
                self.log.warning("Unknown doc type %s" %
                                 td.a['href'].split("=")[-1])
                doctype = None
            if doctype:
                if attachment:
                    filename = self.store.downloaded_path(
                        basefile, attachment=attachment + doctype)
                else:
                    filename = self.store.downloaded_path(basefile, attachment="index" + doctype)
                self.log.debug("%s: downloading attachment %s" % (basefile, filename))
                self.download_if_needed(url, basefile, filename=filename)

        if mainattachment == None:
            entry = DocumentEntry(self.store.documententry_path(basefile))
            now = datetime.now()
            entry.orig_url = url
            if created:
                entry.orig_created = now
            if updated:
                entry.orig_updated = now
            if checked:
                entry.orig_checked = now
            entry.save()

        return updated

    # Correct some invalid identifiers spotted in the wild:
    # 1999/20 -> 1999/2000
    # 2000/2001 -> 2000/01
    # 1999/98 -> 1999/2000
    def sanitize_basefile(self, basefile):
        (y1, y2, idx) = re.split("[:/]", basefile)
        assert len(
            y1) == 4, "Basefile %s is invalid beyond sanitization" % basefile
        if y1 == "1999" and y2 != "2000":
            sanitized = "1999/2000:" + idx
            self.log.warning("Basefile given as %s, correcting to %s" %
                             (basefile, sanitized))
        elif (y1 != "1999" and
              (len(y2) != 2 or  # eg "2000/001"
               int(y1[2:]) + 1 != int(y2))):  # eg "1999/98

            sanitized = "%s/%02d:%s" % (y1, int(y1[2:]) + 1, idx)
            self.log.warning("Basefile given as %s, correcting to %s" %
                             (basefile, sanitized))
        else:
            sanitized = basefile
        return sanitized

    # For parsing:
    # 1999/94 and 1994/95 has only plaintext
    # 1995/96 to 2006/07 has plaintext + doc
    # 2007/08 onwards has plaintext, doc and pdf
    @managedparsing
    def parse(self, doc):
        try:

            # prefer PDF or Word files over the plaintext-containing HTML files
            # FIXME: PDF or Word files are now stored as attachments
            htmlfile = self.store.downloaded_path(doc.basefile)
            
            pdffile = self.store.path(doc.basefile, 'downloaded', '.pdf')
            
            wordfiles = (self.store.path(doc.basefile, 'downloaded', '.doc'),
                         self.store.path(doc.basefile, 'downloaded', '.docx'),
                         self.store.path(doc.basefile, 'downloaded', '.wpd'),
                         self.store.path(doc.basefile, 'downloaded', '.rtf'))

            # check if ANY of these exist
            if not filter(None, [os.path.exists(f) for f in wordfiles + (htmlfile, pdffile)]):
                raise errors.NoDownloadedFileError("File '%s' (or any .pdf/.doc/.docx/.wpd/.rdf variant) not found" % htmlfile)
            
            wordfile = None
            for f in wordfiles:
                if os.path.exists(f):
                    wordfile = f
            
            doc.uri = self.canonical_uri(doc.basefile)
            d = Describer(doc.meta, doc.uri)
            d.rdftype(self.rdf_type)

            # if we lack a .pdf file, use Open/LibreOffice to convert any
            # .wpd or .doc file to .pdf first
            if (wordfile
                    and not os.path.exists(pdffile)):
                intermediate_pdf = self.store.path(
                    doc.basefile, "intermediate", ".pdf")
                if not os.path.exists(intermediate_pdf):
                    cmdline = "%s --headless -convert-to pdf -outdir '%s' %s" % (self.config.get('soffice', 'soffice'),
                                                                                 os.path.dirname(
                                                                                     intermediate_pdf),
                                                                                 wordfile)
                    self.log.debug(
                        "%s: Converting to PDF: %s" % (doc.basefile, cmdline))
                    (ret, stdout, stderr) = util.runcmd(
                        cmdline, require_success=True)
                pdffile = intermediate_pdf

            if os.path.exists(pdffile):
                self.log.debug("%s: Using %s" % (doc.basefile, pdffile))
                intermediate_dir = os.path.dirname(
                    self.store.path(doc.basefile, 'intermediate', '.foo'))
                keep_xml = "bz2" if self.config.compress == "bz2" else True
                pdfreader = PDFReader(filename=pdffile,
                                      workdir=intermediate_dir,
                                      keep_xml=keep_xml)
                self.parse_from_pdfreader(pdfreader, doc)
            else:
                downloaded_path = self.store.downloaded_path(doc.basefile)
                intermediate_path = self.store.path(
                    doc.basefile, 'intermediate', '.txt')
                self.log.debug("%s: Using %s (%s)" % (doc.basefile,
                               downloaded_path, intermediate_path))
                if not os.path.exists(intermediate_path):
                    html = codecs.open(
                        downloaded_path, encoding="iso-8859-1").read()
                    util.writefile(intermediate_path, util.extract_text(
                        html, '<pre>', '</pre>'), encoding="utf-8")
                textreader = TextReader(intermediate_path, encoding="utf-8")
                self.parse_from_textreader(textreader, doc)
                # How to represent that one XHTML doc was created from
                # plaintext, and another from PDF? create a bnode
                # representing the source prov:wasDerivedFrom and set its
                # dcterms:format to correct mime type

            d.value(self.ns['prov'].wasGeneratedBy, self.qualified_class_name())
            self.infer_triples(d, doc.basefile)
            return True
        except Exception as e:
            err = errors.ParseError(str(e))
            if isinstance(e, IOError):
                err.dummyfile = self.store.parsed_path(doc.basefile)
            raise err

    def parse_from_pdfreader(self, pdfreader, doc):
        parser = offtryck_parser(preset='proposition')
        doc.body = parser.parse(pdfreader.textboxes(offtryck_gluefunc))

    def parse_from_textreader(self, textreader, doc):
        describer = Describer(doc.meta, doc.uri)
        for p in textreader.getiterator(textreader.readparagraph):
            # print "Handing %r (%s)" % (p[:40], len(doc.body))
            if not p.strip():
                continue
            elif not doc.body and 'Obs! Dokumenten i denna databas kan vara ofullständiga.' in p:
                continue
            elif not doc.body and p.strip().startswith("Dokument:"):
                # We already know this
                continue
            elif not doc.body and p.strip().startswith("Titel:"):
                describer.value(
                    self.ns['dcterms'].title, util.normalize_space(p[7:]))
            else:
                doc.body.append(Preformatted([p]))


class PropRiksdagen(Riksdagen):
    alias = "propriksdagen"
    rdf_type = RPUBL.Proposition
    document_type = Riksdagen.PROPOSITION

# inherit list_basefiles_for from CompositeStore, basefile_to_pathfrag
# from SwedishLegalStore)
class PropositionerStore(CompositeStore, SwedishLegalStore):
    pass

class Propositioner(CompositeRepository, SwedishLegalSource):
    subrepos = PropRegeringen, PropTrips, PropRiksdagen
    alias = "prop"
    xslt_template = "res/xsl/forarbete.xsl"
    storage_policy = "dir"
    rdf_type = RPUBL.Proposition
    documentstore_class = PropositionerStore
    sparql_annotations = None # don't even bother creating an annotation file
    def tabs(self, primary=False):
        return [('Förarbeten', self.dataset_uri())]
