# -*- coding: utf-8 -*-

# DOCUMENTATION EPUB AT:
# http://www.idpf.org/doc_library/epub/OPF_2.0.1_draft.htm#Section1.3.3

import io
import os
import re
from xml.dom import minidom
from zipfile import ZipFile

from pyinfoepub.parsers.parsers_epub import *  # NOQA


class PyInfoEpub(object):
    def __init__(self, filename):
        self.epub_filename = filename
        self.epub_content = {}
        self.deprecated_flag = False
        self.opf = None

    def get_info(self):
        try:
            self.unzip()

            self.get_opf()
            self.get_ncx()
            self.check_deprecated()

            return self.extract_info()
        except Exception as e:
            print(e)

    def unzip(self):
        '''prepares the ZIP object'''
        with ZipFile(self.epub_filename, "r") as zfile:
            self.zfilelist = zfile.infolist()
            for info in zfile.infolist():
                self.epub_content[info.filename] = io.BytesIO(zfile.read(info))

    def get_opf(self):
        '''OPF file contains book information (author, publisher, etc.) and
        a list of all files in the book package.'''
        xmlstring = self.read_section('META-INF/container.xml')
        xmldoc = minidom.parseString(xmlstring)
        opfname = xmldoc.getElementsByTagName("rootfile").item(0).getAttribute("full-path")

        self.opf = minidom.parseString(self.read_section(opfname))

    def read_section(self, section_name):
        '''reads and decode a specific section from previously loaded epub_content'''
        return self.epub_content[section_name].read().decode('UTF-8')

    def get_ncx(self):
        '''NCX file tells the sequence and organization
        (parts, chapters or sections) of XHTML documents in a book.'''
        reslist = [
            f for f in self.epub_content.keys() if re.match(r'.*\/.*\.ncx$', f)]
        ncx_filename = reslist[0] if reslist else False

        self.ncx = minidom.parseString(
            self.read_section(ncx_filename)) if ncx_filename else None

    def check_deprecated(self):
        '''checks if the EPUB file uses deprecated dc-metadata or just metadata'''
        self.deprecated_flag = bool(self.opf.getElementsByTagName("dc-metadata"))

    def extract_info(self):
        '''displays the formatted info for the EPUB'''
        pob = Parser(self.opf, self.deprecated_flag)

        content = {}
        content['filename'] = os.path.basename(self.epub_filename)

        content['book_title'] = pob.change(ParserBookTitle).parse()

        content['creators'] = pob.change(ParserCreator).parse()
        content['main_subject'] = pob.change(ParserSubject).parse()
        content['description'] = pob.change(ParserDescription).parse()
        content['publisher'] = pob.change(ParserPublisher).parse()
        content['date'], content['event'] = pob.change(ParserDate).parse()
        content['type'] = pob.change(ParserType).parse()
        content['format'] = pob.change(ParserFormat).parse()
        content['subjects'], content['identifiers'] = pob.change(ParserIdentifier).parse()
        content['language'] = pob.change(ParserLanguage).parse()
        content['source'] = pob.change(ParserSource).parse()
        content['relation'] = pob.change(ParserRelation).parse()
        content['coverage'] = pob.change(ParserCoverage).parse()
        content['rights'] = pob.change(ParserRights).parse()

        content['manifest'] = pob.change(ParserManifest).parse()

        pob = Parser(self.ncx)
        content['toc'] = pob.change(ParserTOC).parse()

        return content
