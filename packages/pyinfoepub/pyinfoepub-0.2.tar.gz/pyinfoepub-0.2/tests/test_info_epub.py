#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TEST INFO EPUB
----------------------------------

Tests for info_epub module
"""

import copy
from io import BytesIO
import unittest
from xml.dom import minidom

from pyinfoepub.infoepub import PyInfoEpub
# TESTS ARE BASED ON THIS SAMPLE
EPUB_SAMPLE_FILE = './samples/Franz Kafka - Metamorphosis.epub'


class InfoEpubTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.info_epub = PyInfoEpub(EPUB_SAMPLE_FILE)

    def test_get_info_check_keys(self):
        pyinfo = copy.deepcopy(self.info_epub)
        output = pyinfo.get_info()

        expected_keys = ['filename', 'book_title', 'creators', 'main_subject', 'description',
        'publisher', 'date', 'type', 'format', 'subjects', 'language', 'source', 'relation',
        'coverage', 'rights', 'manifest', 'toc']
        
        for key_name in expected_keys:
            self.assertTrue(key_name in output)

    def test_check_deprecated(self):
        pyinfo = copy.deepcopy(self.info_epub)
        pyinfo.unzip()
        pyinfo.get_opf()
        pyinfo.check_deprecated()
        self.assertFalse(pyinfo.deprecated_flag)

    def test_get_ncx(self):
        pyinfo = copy.deepcopy(self.info_epub)
        pyinfo.unzip()
        pyinfo.get_ncx()
        self.assertIsInstance(pyinfo.ncx, minidom.Document)

    def test_get_opf(self):
        pyinfo = copy.deepcopy(self.info_epub)
        pyinfo.unzip()
        pyinfo.get_opf()
        self.assertIsInstance(pyinfo.opf, minidom.Document)

    def test_info_epub_after_init(self):
        self.assertEqual(self.info_epub.epub_filename, EPUB_SAMPLE_FILE)
        self.assertEqual(
            self.info_epub.epub_content, {}, 'Content should be an empty dict.')
        self.assertEqual(self.info_epub.opf, None, 'OPF should be None.')
        self.assertFalse(
            self.info_epub.deprecated_flag, 'Deprecated flag should be False.')

    def test_unzip_should_produce_dict_of_bytes(self):
        self.info_epub.unzip()
        for k, v in self.info_epub.epub_content.items():
            self.assertIsInstance(v, BytesIO)

    def test_unzip_invalid_filename(self):
        self.invalid_info_epub = PyInfoEpub('invalid.epub')
        self.assertRaises(FileNotFoundError, self.invalid_info_epub.unzip)

    def setUp(self):
        pass

    def tearDown(self):
        pass


def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
