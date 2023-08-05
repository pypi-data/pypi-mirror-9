#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TEST TEMPLATE CLI
----------------------------------

Tests a specific template
"""

import unittest

from pyinfoepub.templates.cli import TemplateCLI

class TemplateCliTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        #self.main_parser = Parser(self.opf_content, deprecated=False)
        pass

    def test_init_content_keys_uppercase(self):
        content_test = {'key1':1, 'key2':2}
        expected = {'KEY1':1, 'KEY2':2}
        
        tcli = TemplateCLI(content=content_test)
        self.assertDictEqual(tcli.content, expected)
 
    def test_extract_placeholders(self):
        template = """{{PLACEHOLDER_1}} and {{PLACEHOLDER_2}} {NOT_PLACEHOLDER} some text"""
        
        tcli = TemplateCLI({}, template)
        
        placeholders = tcli.extract_placeholders(template)
        self.assertEqual(placeholders,['{{PLACEHOLDER_1}}', '{{PLACEHOLDER_2}}'] )

    def test_render_separators(self):
        template = """{SEP_LINE} and some other {SEP_LINE}"""
        
        tcli = TemplateCLI({}, template)
        tcli.render_separators()

    def test_render_single_elements(self):
        template = """{{SINGLE_ELEM1}}|Lorem|{{SINGLE_ELEM2}}|Ipsum|{{COMPLEX_ELEM|m}}"""
        out_template = """Test|Lorem|Test|Ipsum|{{COMPLEX_ELEM|m}}"""
        
        input_content = {'single_elem1': 'Test', 'single_elem2': 'Test'}
        
        tcli = TemplateCLI(input_content, template)
        tcli.render_single_elements()
        
        self.assertEqual(tcli.tpl, out_template)

    def test_render_single_elements_missing_key(self):
        template = """{{SINGLE_ELEM1}}|Lorem|{{MISING_ELEM}}|Ipsum|{{COMPLEX_ELEM|m}}"""
        out_template = """Test|Lorem||Ipsum|{{COMPLEX_ELEM|m}}"""
        
        input_content = {'single_elem1': 'Test'}
        
        tcli = TemplateCLI(input_content, template)
        tcli.render_single_elements()
        
        self.assertEqual(tcli.tpl, out_template)

    def test_render_list_elements(self):
        template = """REPLACE REPLACE REPLACE Lorem Ipsum REPLACE"""
        out_template = """one, two one, two one, two Lorem Ipsum one, two"""
        
        cph = "REPLACE"
        replacement = ["one", "two"]
        
        tcli = TemplateCLI({}, template)
        tcli.render_list_elements(cph, replacement)

        self.assertEqual(tcli.tpl, out_template)

    def test_render_custom_identifiers(self):
        template = """REPLACE"""
        out_template = """(Scheme1:Ident1) some_id\n(Scheme2:Ident2) some_id"""
        
        cph = "REPLACE"
        replacement = [
            {'scheme':'Scheme1', 'ident':'Ident1', 'id':'some_id'},
            {'scheme':'Scheme2', 'ident':'Ident2', 'id':'some_id'}
        ]
        
        tcli = TemplateCLI({}, template)
        tcli.render_custom_identifiers(cph, replacement)

        self.assertEqual(tcli.tpl, out_template)

    def test_render_custom_manifest(self):
        template = """REPLACE"""
        out_template = \
            "some_id              MediaType1                          http://example.com\n" \
            "some_id              MediaType2                          http://example.com"
        
        cph = "REPLACE"
        replacement = [
            {'media_type':'MediaType1', 'href':'http://example.com', 'id':'some_id'},
            {'media_type':'MediaType2', 'href':'http://example.com', 'id':'some_id'}
        ]
        
        tcli = TemplateCLI({}, template)
        tcli.render_custom_manifest(cph, replacement)

        self.assertEqual(tcli.tpl, out_template)

    def test_render_custom_toc(self):
        template = """REPLACE"""
        out_template = \
            "    1 Chapter I                          \n" \
            "    2 Chapter II                         "
            
        cph = "REPLACE"
        replacement = [
            {'order':'1', 'chapter':'Chapter I'},
            {'order':'2', 'chapter':'Chapter II'}
        ]
        
        tcli = TemplateCLI({}, template)
        tcli.render_custom_toc(cph, replacement)

        self.assertEqual(tcli.tpl, out_template)

    def test_render_complex_element(self):
        template = \
            "Creator:       {{CREATORS|c}}\n" \
            "Main Subject:  {{MAIN_SUBJECT|c}}\n" \
            "Subject(s):    {{SUBJECTS|c}}\n" \
            "Identifier(s):\n" \
            "{{IDENTIFIERS|c}}\n" \
            "Language:     {{LANGUAGE|c}}\n" \
            "FILES INFORMATION\n" \
            "{{MANIFEST|c}}\n" \
            "TOC INFORMATION\n" \
            "{{TOC|c}}"

        out_template = \
            "Creator:       Franz Kafka\n" \
            "Main Subject:  Psychological fiction, Metamorphosis -- Fiction\n" \
            "Subject(s):    Psychological fiction, Metamorphosis -- Fiction\n" \
            "Identifier(s):\n" \
            "(URI:http://www.gutenberg.org/ebooks/5200) id\n" \
            "Language:     en\n" \
            "FILES INFORMATION\n" \
            "item1                text/css                            pgepub.css\n" \
            "TOC INFORMATION\n" \
            "    1 Metamorphosis Franz Kafka          \n" \
            "    2 Translated by David Wyllie         "
                    
        input_content = {
            'creators': ['Franz Kafka'], 
            'main_subject': ['Psychological fiction', 'Metamorphosis -- Fiction'],
            'subjects': ['Psychological fiction', 'Metamorphosis -- Fiction'],
            'identifiers': [{'scheme': 'URI', 'ident': 'http://www.gutenberg.org/ebooks/5200', 'id': 'id'}],
            'language': ['en'],
            'manifest': [{'href': 'pgepub.css', 'media_type': 'text/css', 'id': 'item1'}],
            'toc': [{'order': '1', 'chapter': 'Metamorphosis Franz Kafka'}, {'order': '2', 'chapter': 'Translated by David Wyllie'}],
            }
        
        tcli = TemplateCLI(input_content, template)
        tcli.render_complex_elements()

        self.assertEqual(tcli.tpl, out_template)

    def test_render_complex_element_missing_content_key(self):
        template = "Missing input for this placeholder:{{LANGUAGE|c}}"

        out_template = "Missing input for this placeholder:"
        
        tcli = TemplateCLI({}, template)
        tcli.render_complex_elements()

        self.assertEqual(tcli.tpl, out_template)

    def test_render_complex_element_invalid_placeholder(self):
        template = "Invalid Placeholder: {{INVALID_PLACEHOLDER|c}}"

        tcli = TemplateCLI({}, template)
        
        self.assertRaises(KeyError, tcli.render_complex_elements)


    def tearDown(self):
        pass

    
    
def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
