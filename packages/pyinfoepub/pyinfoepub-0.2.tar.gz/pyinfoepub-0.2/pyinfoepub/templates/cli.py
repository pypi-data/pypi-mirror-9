# -*- coding: utf-8 -*-

import re

# TEMPLATE ELEMENTS
# {SEP_LINE} - special separators lines
# {{KEY}} - simple replacement by key
# {{KEY|c}} - complex replacement; those are mapped inside 'render_complex_elements'

TEMPLATE = """
{SEP_LINE}
GENERAL INFORMATION\n
Filename: {{FILENAME}}\n
{SEP_LINE}
BOOK INFORMATION\n
Title:         {{BOOK_TITLE}}
Creator:       {{CREATORS|c}}
Main Subject:  {{MAIN_SUBJECT|c}}
Description:   {{DESCRIPTION}}
Publisher:     {{PUBLISHER}}
Date:          {{DATE}} {{EVENT}}
Type:          {{TYPE}}
Format:        {{FORMAT}}
Subject(s):    {{SUBJECTS|c}}
Identifier(s):
{{IDENTIFIERS|c}}
Language:     {{LANGUAGE|c}}
Source:       {{SOURCE}}
Relation:     {{RELATION}}
Coverage:     {{COVERAGE}}
Rights:       {{RIGHTS}}

{SEP_LINE}
FILES INFORMATION\n
{{MANIFEST|c}}

{SEP_LINE}
TOC INFORMATION\n
{{TOC|c}}

{SEP_LINE}
"""


class TemplateCLI(object):

    def __init__(self, content={}, template=None):
        # we make sure we have all the keys UPPERCASE for content
        self.content = dict((k.upper(), v) for k, v in content.items())
        self.tpl = template if template else TEMPLATE
        self.placeholders = self.extract_placeholders(self.tpl)

    def render(self, elements={}):
        self.render_separators()
        self.render_single_elements()
        self.render_complex_elements()

        print(self.tpl)

    def render_single_elements(self):
        '''single placeholder is something as {{KEY}} without custom separator | '''
        single_placeholders = [ph for ph in self.placeholders if ph.find("|") == -1]
        for sph in single_placeholders:
            key = sph.replace('{', '').replace('}', '')
            try:
                replacement = self.content[key]
            except KeyError:
                replacement = ''
            finally:
                self.tpl = self.tpl.replace(sph, replacement)

    def render_complex_elements(self):
        '''complex placeholder is something as {{KEY|c}}'''
        mapper = {
            'CREATORS': self.render_list_elements,
            'MAIN_SUBJECT': self.render_list_elements,
            'SUBJECTS': self.render_list_elements,
            'LANGUAGE': self.render_list_elements,
            'IDENTIFIERS': self.render_custom_identifiers,
            'MANIFEST': self.render_custom_manifest,
            'TOC': self.render_custom_toc
        }

        complex_placeholders = [ph for ph in self.placeholders if ph.find("|") != -1]
        for cph in complex_placeholders:
            ckey = cph.replace('{', '').replace('}', '')
            key, complex_ident = ckey.split("|")

            try:
                replacement = self.content[key]
            except KeyError:
                replacement = []
            finally:
                mapper[key](cph, replacement)

    def extract_placeholders(self, tpl):
        return re.findall('({{.*?}})', tpl)

    # GENERIC RENDERERS BELOW
    def render_separators(self):
        self.tpl = self.tpl.replace("{SEP_LINE}", "=" * 50)

    def render_list_elements(self, cph, replacement_lst):
        self.tpl = self.tpl.replace(cph, ", ".join(replacement_lst))

    # CUSTOM RENDERERS BELOW
    def render_custom_identifiers(self, cph, replacement):
        content = []
        for r in replacement:
            content.append("({0}:{1}) {2}".format(r['scheme'], r['ident'], r['id']))
        self.tpl = self.tpl.replace(cph, "\n".join(content))

    def render_custom_manifest(self, cph, replacement):
        content = []
        for r in replacement:
            content.append("{0:20s} {1:35s} {2}".format(r['id'], r['media_type'], r['href']))
        self.tpl = self.tpl.replace(cph, "\n".join(content))

    def render_custom_toc(self, cph, replacement):
        content = []
        for r in replacement:
            content.append("{0:>5s} {1:35s}".format(r['order'], r['chapter']))
        self.tpl = self.tpl.replace(cph, "\n".join(content))
