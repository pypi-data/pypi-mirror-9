# -*- coding: utf-8 -*-


class Parser(object):

    def __init__(self, content, deprecated=False):
        self.deprecated_flag = deprecated
        if not content:
            raise Exception("Some content should be provided for Parser.")

        self.content = content
        self.parser = None

    def change(self, parserFunc):
        self.parser = parserFunc
        return self

    def parse(self):
        return self.parser(self)

    def get_elem(self, fieldname):
        fldname = fieldname.capitalize() if self.deprecated_flag else fieldname
        return self.content.getElementsByTagNameNS("*", fldname)


# Different parsers to be used with the main module Parser
def ParserBookTitle(obj):
    elem = obj.get_elem('title').item(0)
    title = elem.childNodes[0].nodeValue if elem else ''

    return title


def ParserCreator(obj):
    creators = [
        e.childNodes[0].nodeValue for e in obj.get_elem('creator') if e]

    return creators


def ParserSubject(obj):
    subjects = [
        e.childNodes[0].nodeValue for e in obj.get_elem('subject') if e]

    return subjects


def ParserDescription(obj):
    elem = obj.get_elem('description').item(0)
    description = elem.childNodes[0].nodeValue if elem else ''

    return description


def ParserPublisher(obj):
    elem = obj.get_elem('publisher').item(0)
    publisher = elem.childNodes[0].nodeValue if elem else ''

    return publisher


def ParserDate(obj):
    elem = obj.get_elem('date').item(0)
    date = elem.childNodes[0].nodeValue if elem else ''
    event = elem.getAttribute("event") if elem else ''  # optional

    return (date, event)


def ParserType(obj):
    elem = obj.get_elem('type').item(0)
    type = elem.childNodes[0].nodeValue if elem else ''

    return type


def ParserFormat(obj):
    elem = obj.get_elem('format').item(0)
    formatel = elem.childNodes[0].nodeValue if elem else ''

    return formatel


def ParserIdentifier(obj):
    subjects = []
    subject_elem = obj.get_elem('subject')
    if subject_elem:
        subjects = [e.childNodes[0].nodeValue for e in subject_elem if e]

    idents = []
    identifier = obj.get_elem('identifier')
    if identifier:
        for ielem in identifier:
            ident = ielem.childNodes[0].nodeValue
            scheme = ielem.getAttribute("opf:scheme")
            id = ielem.getAttribute("id")
            idents.append({'scheme': scheme, 'ident': ident, 'id': id})

    return (subjects, idents)


def ParserLanguage(obj):
    lang = [e.childNodes[0].nodeValue for e in obj.get_elem('language') if e]

    return lang


def ParserSource(obj):
    elem = obj.get_elem('source').item(0)
    source = elem.childNodes[0].nodeValue if elem else ''

    return source


def ParserRelation(obj):
    elem = obj.get_elem('relation').item(0)
    relation = elem.childNodes[0].nodeValue if elem else ''

    return relation


def ParserCoverage(obj):
    elem = obj.get_elem('coverage').item(0)
    coverage = elem.childNodes[0].nodeValue if elem else ''

    return coverage


def ParserRights(obj):
    elem = obj.get_elem('rights').item(0)
    rights = elem.childNodes[0].nodeValue if elem else ''

    return rights


def ParserManifest(obj):
    result = []
    elem = obj.get_elem('manifest').item(0)
    if elem.hasChildNodes():
        for e in elem.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                id = e.getAttribute("id")
                href = e.getAttribute("href")
                media_type = e.getAttribute("media-type")
                result.append(
                    {'id': id, 'href': href, 'media_type': media_type})

    return result


def ParserTOC(obj):
    '''The NCX file parsing'''
    result = []
    nav_points = obj.content.getElementsByTagName('navPoint')

    for np in nav_points:
        order = np.getAttribute('playOrder')
        chapter = np.getElementsByTagName('navLabel').item(0)\
                    .getElementsByTagName('text').item(0).firstChild.nodeValue
        result.append({'order': order, 'chapter': chapter})

    return result
