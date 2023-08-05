# Copyright 2013 Sam Kleinman, Cyborg Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import textwrap
import logging

from rstcloth.cloth import Cloth

logger = logging.getLogger("rstcloth")

def fill(string, first=0, hanging=0, wrap=True):
    first_indent = ' ' * first
    hanging_indent = ' ' * hanging

    if wrap is True:
        return textwrap.fill(string,
                             width=72,
                             break_on_hyphens=False,
                             break_long_words=False,
                             initial_indent=first_indent,
                             subsequent_indent=hanging_indent)
    else:
        content = string.split('\n')
        if first == hanging:
            return '\n'.join([ first_indent + line for line in content ])
        elif first > hanging:
            indent_diff = first - hanging
            o = indent_diff * ' '
            o += '\n'.join([ hanging_indent + line for line in content ])
            return o
        elif first < hanging:
            indent_diff = hanging - first
            o = '\n'.join([ hanging_indent + line for line in content ])
            return o[indent_diff:]

def _indent(content, indent):
    if indent == 0:
        return content
    else:
        indent = ' ' * indent
        if isinstance(content, list):
            return [ ''.join([indent, line]) for line in content ]
        else:
            return ''.join([indent, content])

class RstCloth(Cloth):
    def __init__(self):
        self._data = []

    def _add(self, content, block=None):
        if block is not None:
            logger.warning('block "{0}" is no longer supported'.format(block))

        if isinstance(content, list):
            self._data.extend(content)
        else:
            self._data.append(content)

    def newline(self, count=1, block=None):
        if isinstance(count, int):
            if count == 1:
                self._add('')
            else:
                # subtract one because every item gets one \n for free.
                self._add('\n' * (count - 1))
        else:
            raise Exception("Count of newlines must be a positive int.")

    def directive(self, name, arg=None, fields=None, content=None, indent=0, wrap=True, block=None):
        o = [ ]

        o.append('.. {0}::'.format(name))

        if arg is not None:
            o[0] += ' ' + arg

        if fields is not None:
            for k, v in fields:
                o.append(_indent(':' + k + ': ' + str(v), 3))

        if content is not None:
            o.append('')

            if isinstance(content, list):
                o.extend(_indent(content, 3))
            else:
                o.append(_indent(content, 3))

        self._add(_indent(o, indent))

    @staticmethod
    def role(name, value, text=None):
        if isinstance(name, list):
            name = ':'.join(name)

        if text is None:
            return ':{0}:`{1}`'.format(name, value)
        else:
            return ':{0}:`{2} <{1}>`'.format(name, value, text)

    @staticmethod
    def bold(string):
        return '**{0}**'.format(string)

    @staticmethod
    def emph(string):
        return '*{0}*'.format(string)

    @staticmethod
    def pre(string):
        return '``{0}``'.format(string)

    @staticmethod
    def inline_link(text, link):
        return '`{0} <{1}>`_'.format(text, link)

    @staticmethod
    def footnote_ref(name):
        return '[#{0}]'.format(name)

    @staticmethod
    def _paragraph(content, wrap=True):
        return [ i.strip() for i in fill(content, wrap=wrap).split('\n') ]

    def replacement(self, name, value, indent=0, block=None):
        output = '.. |{0}| replace:: {1}'.format(name, value)
        self._add(_indent(output, indent))

    def codeblock(self, content, indent=0, wrap=True, language=None, block=None):
        if language is None:
            o = [ '::', _indent(content, 3) ]
            self._add(_indent(o, indent))
        else:
            self.directive(name='code-block', arg=language, content=content, indent=indent)

    def footnote(self, ref, text, indent=0, wrap=True, block=None):
        self._add(fill('.. [#{0}] {1}'.format(ref, text), indent, indent + 3, wrap))

    def definition(self, name, text, indent=0, wrap=True, bold=False, block=None):
        o = []

        if bold is True:
            name = self.bold(name)

        o.append(_indent(name, indent))
        o.append(fill(text, indent + 3, indent + 3, wrap=wrap))

        self._add(o)

    def li(self, content, bullet='-', indent=0, wrap=True, block=None):
        bullet = bullet + ' '
        hanging_indent_len = indent + len(bullet)
        hanging_indent = ' ' * hanging_indent_len

        if isinstance(content, list):
            content = bullet + '\n'.join(content)
            self._add(fill(content, indent, indent + hanging_indent_len, wrap))
        else:
            content = bullet + fill(content, 0, len(bullet), wrap)
            self._add(fill(content, indent, indent, wrap))

    def field(self, name, value, indent=0, wrap=True, block=None):
        output = [ ':{0}:'.format(name) ]

        if len(name) + len(value) < 60:
            output[0] += ' ' + value
            final = True
        else:
            output.append('')
            final = False

        if wrap is True and final is False:
            content = fill(value, wrap=wrap).split('\n')
            for line in content:
                output.append(_indent(line, 3))

        if wrap is False and final is False:
            output.append(_indent(value, 3))

        for line in output:
            self._add(_indent(line, indent))

    def ref_target(self, name, indent=0, block=None):
        o = '.. _{0}:'.format(name)
        self._add(_indent(o, indent))

    def content(self, content, indent=0, wrap=True, block=None):
        if isinstance(content, list):
            for line in content:
                self._add(_indent(line, indent))
        else:
            lines = self._paragraph(content, wrap)

            for line in lines:
                self._add(_indent(line, indent))

    def title(self, text, char='=', indent=0, block=None):
        line = char * len(text)
        self._add(_indent([line, text, line], indent))

    def heading(self, text, char, indent=0, block=None):
        self._add(_indent([text, char * len(text)], indent))

    def h1(self, text, indent=0, block=None):
        self.heading(text, char='=', indent=indent)

    def h2(self, text, indent=0, block=None):
        self.heading(text, char='-', indent=indent)

    def h3(self, text, indent=0, block=None):
        self.heading(text, char='~', indent=indent)

    def h4(self, text, indent=0, block=None):
        self.heading(text, char='+', indent=indent)

    def h5(self, text, indent=0, block=None):
        self.heading(text, char='^', indent=indent)

    def h6(self, text, indent=0, block=None):
        self.heading(text, char=';', indent=indent)
