# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# A abstract base class for fetching documents from data.riksdagen.se

import os
import json
import codecs

import requests
import requests.exceptions
from bs4 import BeautifulSoup
from rdflib import URIRef

from . import SwedishLegalSource
from .swedishlegalsource import offtryck_parser, offtryck_gluefunc, PreambleSection, UnorderedSection
from ferenda import util, errors
from ferenda.decorators import managedparsing, downloadmax
from ferenda.describer import Describer
from ferenda.elements import Paragraph
from ferenda import PDFReader, PDFAnalyzer

class Riksdagen(SwedishLegalSource):
    BILAGA = "bilaga"
    DS = "ds"
    DIREKTIV = "dir"
    EUNAMND_KALLELSE = "kf-lista"
    EUNAMND_PROT = "eunprot"
    EUNAMND_DOK = "eundok"
    EUNAMND_BILAGA = "eunbil"
    FAKTAPROMEMORIA = "fpm"
    FRAMSTALLNING = "frsrdg"
    FOREDRAGNINGSLISTA = "f-lista"
    GRANSKNINGSRAPPORT = "rir"
    INTERPELLATION = "ip"
    KOMMITTEBERATTELSER = "komm"
    MINISTERRADSPROMEMORIA = "minråd"
    MOTION = "mot"
    PROPOSITION = "prop"
    PROTOKOLL = "prot"
    RAPPORT = "rfr"
    RIKSDAGSSKRIVELSE = "rskr"
    FRAGA = "fr"
    SKRIVELSE = "skr"
    SOU = "sou"
    SVAR = "frs"
    SFS = "sfs"
    TALARLISTA = "t-lista"
    UTSKOTTSDOKUMENT = "utskottsdokument"
    YTTRANDE = "yttr"

    # add typ=prop or whatever
    downloaded_suffix = ".xml"
    storage_policy = "dir"

    document_type = None
    start_url = None
    start_url_template = "http://data.riksdagen.se/dokumentlista/?sz=100&sort=d&utformat=xml&typ=%(doctype)s"

    def download(self, basefile=None):
        if basefile:
            return self.download_single(basefile)
        url = self.start_url_template % {'doctype': self.document_type}
        for basefile, url in self.download_get_basefiles(url):
            self.download_single(basefile, url)

    @downloadmax
    def download_get_basefiles(self, start_url):
        self.log.info("Starting at %s" % start_url)
        url = start_url
        done = False
        pagecount = 1
        while not done:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, features="xml")

            subnodes = soup.find_all(lambda tag: tag.name == "subtyp" and
                                     tag.text == self.document_type)
            for doc in [x.parent for x in subnodes]:
                # TMP: Only retrieve old documents
                # if doc.rm.text > "1999":
                #     continue
                if doc.rm is None or doc.nummer is None:
                    # this occasionally happens, although not all the
                    # time for the same document. We can't really
                    # recover from this easily, so we'll just skip and
                    # hope that it doesn't occur on next download.
                    continue
                basefile = "%s:%s" % (doc.rm.text, doc.nummer.text)
                attachment = None
                if doc.tempbeteckning.text:
                    attachment = doc.tempbeteckning.text
                yield (basefile, attachment), doc.dokumentstatus_url_xml.text
            try:
                url = soup.dokumentlista['nasta_sida']
                pagecount += 1
                self.log.info("Getting page #%d" % pagecount)
            except KeyError:
                self.log.info("That was the last page")
                done = True

    def remote_url(self, basefile):
        # FIXME: this should be easy
        digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if "/" in basefile:   # eg 1975/76:24
            year = int(basefile.split("/")[0])
            remainder = year - 1400
        else:                 # eg 1975:6
            year = int(basefile.split(":")[0])
            remainder = year - 1401
        pnr = basefile.split(":")[1]
        base36year = ""
        # since base36 year is guaranteed to be 2 digits, this could
        # be simpler.
        while remainder != 0:
            remainder, i = divmod(remainder, len(digits))
            base36year = digits[i] + base36year
        # FIXME: Map more of these...
        doctypecode = {self.PROPOSITION: "03",
                       self.UTSKOTTSDOKUMENT: "01"}[self.document_type]
        return "http://data.riksdagen.se/dokumentstatus/%s%s%s.xml" % (
            base36year, doctypecode, pnr)

                
    def download_single(self, basefile, url=None):
        attachment = None
        if isinstance(basefile, tuple):
            basefile, attachment = basefile
        if attachment:
            docname = attachment
        else:
            docname = "index"

        if not url:
            url = self.remote_url(basefile)
            if not url:  # remote_url failed
                return False

        xmlfile = self.store.downloaded_path(basefile)
        if not (self.config.refresh or not os.path.exists(xmlfile)):
            self.log.debug("%s already exists" % (xmlfile))
            return False

        existed = os.path.exists(xmlfile)
        self.log.debug("  %s: Downloading to %s" % (basefile, xmlfile))

        updated = self.download_if_needed(url, basefile)

        if existed:
            if updated:
                self.log.info("%s: updated from %s" % (basefile, url))
            else:
                self.log.debug("%s: %s is unchanged, checking files" %
                               (basefile, xmlfile))
        else:
            self.log.info("%s: downloaded from %s" % (basefile, url))
        fileupdated = False
        r = None
        docsoup = BeautifulSoup(open(xmlfile), features="xml")
        dokid = docsoup.find('dok_id').text
        if docsoup.find('dokument_url_html'):
            htmlurl = docsoup.find('dokument_url_html').text
            htmlfile = self.store.downloaded_path(basefile, attachment=docname + ".html")
            self.log.debug("   Downloading to %s" % htmlfile)
            r = self.download_if_needed(htmlurl, basefile, filename=htmlfile)
        elif docsoup.find('dokument_url_text'):
            texturl = docsoup.find('dokument_url_text').text
            textfile = self.store.downloaded_path(basefile, attachment=docname + ".txt")
            self.log.debug("   Downloading to %s" % htmlfile)
            r = self.download_if_needed(texturl, basefile, filename=textfile)
        fileupdated = fileupdated or r

        for b in docsoup.findAll('bilaga'):
            # self.log.debug("Looking for %s, found %s", dokid, b.dok_id.text)
            if b.dok_id.text != dokid:
                continue
            if b.filtyp is None:
                # apparantly this can happen sometimes? Very intermitently, though.
                self.log.warning("Couldn't find filtyp for bilaga %s in %s" % (b.dok_id.text, xmlfile))
                continue
            filetype = "." + b.filtyp.text
            filename = self.store.downloaded_path(basefile, attachment=docname + filetype)
            self.log.debug("   Downloading to %s" % filename)
            try:
                r = self.download_if_needed(b.fil_url.text, basefile, filename=filename)
            except requests.exceptions.HTTPError as e:
                # occasionally we get a 404 even though we shouldn't. Report and hope it goes better next time.
                self.log.error("   Failed: %s" % e)
                continue
            fileupdated = fileupdated or r
            break

        if updated or fileupdated:
            return True  # Successful download of new or changed file
        else:
            self.log.debug(
                "%s and all associated files unchanged" % xmlfile)

    @managedparsing
    def parse(self, doc):
        filename = self.store.downloaded_path(doc.basefile)
        if not os.path.exists(filename):
            raise errors.NoDownloadedFileError("File '%s' not found" % filename)
        htmlfile = self.store.path(doc.basefile, 'downloaded', '.html')
        pdffile  = self.store.path(doc.basefile, 'downloaded', '.pdf')

        intermediate_path = self.store.intermediate_path(doc.basefile,
                                                         attachment=os.path.basename(pdffile))
        intermediate_dir = os.path.dirname(intermediate_path)

        doc.uri = self.canonical_uri(doc.basefile)
        self.log.debug("Set URI to %s (from %s)" % (doc.uri, doc.basefile))
        d = Describer(doc.meta, doc.uri)
        d.rdftype(self.rdf_type)
        d.value(self.ns['prov'].wasGeneratedBy, self.qualified_class_name())
        xsoup = BeautifulSoup(open(self.store.downloaded_path(
            doc.basefile)).read(), "xml")
        d.value(self.ns['dcterms'].title, xsoup.dokument.titel.text, lang="sv")
        d.value(self.ns['dcterms'].issued,
                util.strptime(xsoup.dokument.publicerad.text,
                              "%Y-%m-%d %H:%M:%S").date())
        self.infer_triples(d, doc.basefile)
        identifier = doc.meta.value(URIRef(doc.uri),
                                    self.ns['dcterms'].identifier)
        if identifier:
            identifier = str(identifier)

        if os.path.exists(pdffile):
            hocr_path = self.store.path(doc.basefile, 'intermediate',
                                        '.hocr.html.bz2')
            metrics_path = self.store.path(doc.basefile, 'intermediate',
                                           '.metrics.json')
            plot_path = self.store.path(doc.basefile, 'intermediate',
                                        '.plot.png')
            pdfdebug_path = self.store.path(doc.basefile, 'intermediate',
                                        '.debug.pdf')
            # slight optimization: if we've already performed OCR,
            # then the PDF won't contain regular text -- don't bother
            # trying to parse it as a regular PDF.
            if util.outfile_is_newer([pdffile], hocr_path):
                pdf = PDFReader(filename=pdffile,
                                workdir=intermediate_dir,
                                ocr_lang="swe", keep_xml="bz2")
            else:
                pdf = PDFReader(filename=pdffile,
                                workdir=intermediate_dir,
                                images=False, keep_xml="bz2")
                if pdf.is_empty():
                    self.log.debug("%s: %s contains no text, performing OCR" %
                                   (doc.basefile, pdffile))
                    pdf = PDFReader(filename=pdffile, workdir=intermediate_dir,
                                    ocr_lang="swe", keep_xml="bz2")

            # FIXME: add code to get a customized PDFAnalyzer class here
            # if self.document_type = self.PROPOSITION: 
            analyzer = PDFAnalyzer(pdf)
            # metrics = analyzer.metrics(metrics_path, plot_path, force=self.config.force)
            metrics = analyzer.metrics(metrics_path, plot_path)
            if os.environ.get("FERENDA_DEBUGANALYSIS"):
                self.log.debug("Creating debug version of PDF")
                analyzer.drawboxes(pdfdebug_path, offtryck_gluefunc, metrics=metrics)
            self.log.debug("Parsing with metrics %s" % metrics)

            parser = offtryck_parser(metrics=metrics)
            parser.debug = os.environ.get('FERENDA_FSMDEBUG', False)
            parser.current_identifier = identifier
            doc.body = parser.parse(pdf.textboxes(offtryck_gluefunc))
        else:
            self.log.debug("Loading soup from %s" % htmlfile)
            soup = BeautifulSoup(
                codecs.open(
                    htmlfile, encoding='iso-8859-1', errors='replace').read(),
                )
            self.parse_from_soup(soup, doc)
        return True

    def parse_from_soup(self, soup, doc):
        for block in soup.findAll(['div', 'p', 'span']):
            t = util.normalize_space(''.join(block.findAll(text=True)))
            block.extract()  # to avoid seeing it again
            if t:
                doc.body.append(Paragraph([t]))

    def canonical_uri(self, basefile):
        seg = {self.ns['rpubl'].Proposition: "prop",
               self.ns['rpubl'].Skrivelse: "skr"}
        return self.config.url + "res/%s/%s" % (seg[self.rdf_type], basefile)
