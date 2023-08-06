# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# robotframework-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# robotframework-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with robotframework-tools. If not, see <http://www.gnu.org/licenses/>.

"""robottools.library.libdoc.html

HTML stream wrapper for robottools.libdoc()

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['HTML']

from six.moves.html_parser import HTMLParser

from moretools import isstring


def HTML(Stream, **options):
    """Creates an out `Stream` class wrapper for :func:`robottools.libdoc`,
       which post-processes the generated HTML data
       according to the given :func:`robottools.libdoc` extra `options`.
    """
    exclude_tags = []
    if options.pop('standalone', True) is False:
        exclude_tags += ['html', 'head', 'meta', 'body']
    heading = options.pop('heading', True)
    if heading and heading is not True:
        heading = str(heading)
    elif heading is False:
        exclude_tags += ['h1']
    if options: # anything left?
        raise ValueError(
          "Invalid robottools.libdoc() extra options for 'html' format: %s"
          % repr(options))

    class Parser(HTMLParser, Stream):
        """The actual HTML post-processing out stream class wrapper.
        """
        write = HTMLParser.feed
        # look like a text stream
        encoding = 'utf8'

        # track current element for lookup in self.handle_data()
        tag = None
        attrs = ()

        def __init__(self):
            HTMLParser.__init__(self)
            Stream.__init__(self)

        def handle_starttag(self, tag, attrs):
            if tag not in exclude_tags:
                Stream.write(self, '<%s %s>' % (
                  tag, ' '.join('%s="%s"' % a for a in attrs)))
            # for lookup in self.handle_data
            self.tag = tag
            self.attrs = attrs

        def handle_endtag(self, tag):
            if tag not in exclude_tags:
                Stream.write(self, '</%s>' % tag)
            # there is currently no use case for processing data
            # directly following an end tag
            #==> no stack
            self.tag = None
            self.attrs = ()

        def handle_startendtag(self, tag, attrs):
            if tag not in exclude_tags:
                Stream.write(self, '<%s %s />' % (
                  tag, ' '.join('%s="%s"' % a for a in attrs)))
            # see self.handle_endtag()
            self.tag = None
            self.attrs = ()

        def handle_data(self, text):
            if self.tag not in exclude_tags:
                if self.tag == 'script' \
                  and ('type', 'text/x-jquery-tmpl') in self.attrs:
                    # also process the contents of embedded jQuery templates
                    Parser().feed(text)
                elif self.tag == 'h1' and isstring(heading):
                    # custom override heading
                    Stream.write(self, heading)
                else:
                    Stream.write(self, text)

    return Parser()
