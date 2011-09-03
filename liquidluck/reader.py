#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from xml.dom import minidom
from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst import directives, Directive
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

INLINESTYLES = False
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)
VARIANTS = {
    'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
}


class Pygments(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        # take an arbitrary option if more than one is given
        formatter = self.options and VARIANTS[self.options.keys()[0]] \
                    or DEFAULT
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('code-block', Pygments)
directives.register_directive('sourcecode', Pygments)


class rstParser(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def _plain_text(self, node):
        child = node.firstChild
        if not child:
            return None
        if child.nodeType == node.TEXT_NODE:
            return child.data
        return None

    def _node_to_pairs(self, node):
        '''
        <tr><th class="docinfo-name">Date:</th>
        <td>2011-10-12</td></tr>
        '''
        keyNode = node.firstChild
        key = self._plain_text(keyNode)
        key = key.lower().replace(':','')

        valueNode = node.lastChild

        tag = valueNode.firstChild.nodeName
        if 'ul' == tag or 'ol' == tag:
            value = []
            nodes = valueNode.getElementsByTagName('li')
            for node in nodes:
                value.append(self._plain_text(node))
        else:
            value = self._plain_text(valueNode)
        return key, value

    def read(self):
        f = open(self.filepath)
        print 'open'
        content = f.read()
        f.close()

        extra_setting = {'initial_header_level':'3'}
        parts = publish_parts(
            content, writer_name='html',
            settings_overrides=extra_setting,
        )

        # get docinfo
        docinfo = []
        dom = minidom.parseString(parts['docinfo'].replace('\n',''))
        nodes = dom.getElementsByTagName('tr')
        for node in nodes:
            docinfo.append(self._node_to_pairs(node))

        parts['docinfo'] = docinfo
        return parts


class rstReader(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.parts = rstParser(filepath).read()

    def get_info(self, key, value=None):
        docinfo = dict(self.parts['docinfo'])
        return docinfo.get(key, value)

    @property
    def mtitme(self):
        stat = os.stat(self.filepath)
        return stat.st_mtime

    @property
    def filename(self):
        folder, filename = os.path.split(self.filepath)
        return filename

    @property
    def suffix(self):
        name, suffix = self.filename.split('.')
        return suffix

    @property
    def slug(self):
        name, suffix = self.filename.split('.')
        return name
