#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TEST PARSERS
----------------------------------

Tests for parsers module
"""

import unittest
from xml.dom import minidom

from pyinfoepub.parsers.parsers_epub import *  # NOQA

# TESTS ARE BASED ON THESE SAMPLES
OPF_SAMPLE_FILE = './samples/content.opf'
NCX_SAMPLE_FILE = './samples/toc.ncx'


class ParsersTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(OPF_SAMPLE_FILE, 'r') as opf:
            cls.opf_content = minidom.parseString(opf.read())
        with open(NCX_SAMPLE_FILE, 'r') as ncx:
            cls.ncx = minidom.parseString(ncx.read())

    def setUp(self):
        self.main_parser = Parser(self.opf_content, deprecated=False)

    # MAIN PARSER TESTS
    def test_main_parser_no_content_raise_exception(self):
        self.assertRaises(Exception, Parser, ())
    
    def test_main_parser_change(self):
        def dummy_parser():
            pass
        self.main_parser.change(dummy_parser)
        self.assertIs(dummy_parser, self.main_parser.parser)

    def test_main_parser_change_return_self(self):
        def dummy_parser():
            pass
        returned = self.main_parser.change(dummy_parser)
        self.assertIsInstance(returned, Parser)

    def test_main_parser_parse_method(self):
        def dummy_parser(obj):
            return obj
        self.main_parser.change(dummy_parser)
        returned = self.main_parser.parse()
        self.assertIs(returned, self.main_parser)

    def test_main_parser_get_elem_deprecated_flag_off(self):
        self.main_parser.deprecated_flag = False
        node_list = self.main_parser.get_elem('rights')
        self.assertEqual(node_list.length, 1)

    def test_main_parser_get_elem_deprecated_flag_on(self):
        self.main_parser.deprecated_flag = True
        node_list = self.main_parser.get_elem('rights')
        self.assertEqual(node_list.length, 0)

    # ParserBookTitle
    def test_parser_book_title_should_return_string(self):
        returned = self.main_parser.change(ParserBookTitle).parse()
        self.assertEqual(returned, "Metamorphosis")

    # ParserCreator
    def test_parser_creator_should_return_list(self):
        returned = self.main_parser.change(ParserCreator).parse()
        self.assertIsInstance(returned, list)
        self.assertEqual(returned[0], 'Franz Kafka')

    def test_parser_creator_return_empty_list_for_noresults(self):
        self.set_empty_content()
        returned = self.main_parser.change(ParserCreator).parse()
        self.assertEqual(returned, [])
        self.revert_valid_content()

    # ParserSubject
    def test_parser_subject_should_return_list(self):
        returned = self.main_parser.change(ParserSubject).parse()
        self.assertIsInstance(returned, list)
        self.assertEqual(returned[0], 'Psychological fiction')

    def test_parser_subject_return_empty_list_for_no_results(self):
        self.set_empty_content()
        returned = self.main_parser.change(ParserSubject).parse()
        self.assertEqual(returned, [])
        self.revert_valid_content()

    # ParserDescription
    def test_parser_description_should_return_string(self):
        returned = self.main_parser.change(ParserDescription).parse()
        self.assertEqual(returned, "")

    # ParserPublisher
    def test_parser_publisher_should_return_string(self):
        returned = self.main_parser.change(ParserPublisher).parse()
        self.assertEqual(returned, "")

    # ParserDate
    def test_parser_date_should_return_tuple(self):
        returned = self.main_parser.change(ParserDate).parse()
        self.assertIsInstance(returned, tuple)
        self.assertEqual(returned[0], '2005-08-17')
        self.assertEqual(returned[1], '')

    # ParserType
    def test_parser_type_should_return_string(self):
        returned = self.main_parser.change(ParserType).parse()
        self.assertEqual(returned, "")

    # ParserFormat
    def test_parser_format_should_return_string(self):
        returned = self.main_parser.change(ParserFormat).parse()
        self.assertEqual(returned, "")

    # ParserIdentifier
    def test_parser_identifier_should_return_tuple_of_lists(self):
        returned = self.main_parser.change(ParserIdentifier).parse()
        self.assertIsInstance(returned, tuple)
        self.assertIsInstance(returned[0], list)
        self.assertIsInstance(returned[1], list)

    def test_parser_identifier_subject_element(self):
        returned = self.main_parser.change(ParserIdentifier).parse()[0]
        self.assertEqual(
            returned, ['Psychological fiction', 'Metamorphosis -- Fiction'])

    def test_parser_identifier_idents_element_is_list_of_dict(self):
        returned = self.main_parser.change(ParserIdentifier).parse()[1]
        self.assertEqual(len(returned), 2)

        first_result = returned[0]
        self.assertIn('id', first_result)
        self.assertIn('ident', first_result)
        self.assertIn('scheme', first_result)

    def test_parser_identifier_idents_element_proper_result(self):
        returned = self.main_parser.change(ParserIdentifier).parse()[1]
        expected = {
            'id': 'id', 'ident': 'http://www.gutenberg.org/ebooks/5200', 'scheme': 'URI'}

        self.assertDictEqual(returned[0], expected)

    # ParserLanguage
    def test_parser_language_should_return_list(self):
        returned = self.main_parser.change(ParserLanguage).parse()
        self.assertIsInstance(returned, list)
        self.assertEqual(returned[0], 'en')

    # ParserSource
    def test_parser_source_should_return_string(self):
        returned = self.main_parser.change(ParserSource).parse()
        self.assertEqual(returned, 'http://www.gutenberg.orgfiles/5200/5200-h/5200-h.htm')


    # ParserRelation
    def test_parser_relation_should_return_string(self):
        returned = self.main_parser.change(ParserRelation).parse()
        self.assertEqual(returned, "")

    # ParserCoverage
    def test_parser_coverage_should_return_string(self):
        returned = self.main_parser.change(ParserCoverage).parse()
        self.assertEqual(returned, "")

    # ParserRights
    def test_parser_right_should_return_string(self):
        returned = self.main_parser.change(ParserRights).parse()
        self.assertEqual(
            returned, "Copyrighted. Read the copyright notice inside this book for details.")

    # ParserManifest
    def test_parser_manifest_should_return_list_of_dictionaries(self):
        returned = self.main_parser.change(ParserManifest).parse()
        self.assertIsInstance(returned, list)
        self.assertIsInstance(returned[0], dict)

    def test_parser_manifest_proper_dictionary_structure(self):
        returned = self.main_parser.change(ParserManifest).parse()[0]
        self.assertIn('id', returned)
        self.assertIn('href', returned)
        self.assertIn('media_type', returned)

    def test_parser_manifest_proper_result(self):
        returned = self.main_parser.change(ParserManifest).parse()
        self.assertEqual(len(returned), 4)

        expected = {
            'media_type': 'text/css', 'id': 'item1', 'href': 'pgepub.css'}
        self.assertDictEqual(returned[0], expected)

    # ParserTOC
    def test_parser_toc_should_return_list_of_dictionaries(self):
        self.main_parser.content = self.ncx
        returned = self.main_parser.change(ParserTOC).parse()
        self.assertIsInstance(returned, list)
        self.assertIsInstance(returned[0], dict)

    def test_parser_toc_proper_dictionary_structure(self):
        self.main_parser.content = self.ncx
        returned = self.main_parser.change(ParserTOC).parse()[0]
        self.assertIn('order', returned)
        self.assertIn('chapter', returned)

    def test_parser_toc_proper_result(self):
        self.main_parser.content = self.ncx
        returned = self.main_parser.change(ParserTOC).parse()
        self.assertEqual(len(returned), 5)

        expected = {'chapter': 'Metamorphosis Franz Kafka', 'order': '1'}
        self.assertDictEqual(returned[0], expected)

        expected = {'chapter': 'I', 'order': '3'}
        self.assertDictEqual(returned[2], expected)

    def test_parser_subject(self):
        pass

    def tearDown(self):
        pass

    # Helpers
    def set_empty_content(self):
        """Setup an empty xml content for the main parser"""
        self.main_parser.content = minidom.parseString(
            "<?xml version='1.0' encoding='UTF-8'?><package></package>")

    def revert_valid_content(self):
        self.main_parser.content = self.opf_content


def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
