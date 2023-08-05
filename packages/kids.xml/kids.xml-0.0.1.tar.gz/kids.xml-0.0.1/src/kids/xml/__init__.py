# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import locale
import re

from xml.sax.saxutils import quoteattr, escape
from lxml import etree, objectify

import kids.file as kf


PY3 = sys.version_info[0] >= 3


def xml2string(content, xml_declaration=True):
    """Render a ElementTree to a string with some default options

    The output should be pretty printed.

    """
    ## Can't rely on lxml pretty_printing it seems... It won't
    ## pretty print some elements for some obscure reasons
    # xml_string = etree.tostring(content,
    #                    pretty_print=True,
    #                    xml_declaration=True,
    #                    encoding="utf-8")

    ## Can't rely on prettyxml as it will insert some new lines in
    ## fields.
    # import xml.dom.minidom
    # xml = xml.dom.minidom.parseString(xml_string)
    # return xml.toprettyxml(indent="  ")

    from kids.sh import wrap
    content = etree.tostring(content, encoding="utf-8")
    if PY3:
        content = content.decode(locale.getpreferredencoding())
    f = kf.tmpfile(content)
    try:
        output = wrap("xmllint --format %r --encode %s" % (f, "utf-8"))
    finally:
        kf.rm(f)
    return output if xml_declaration else output.split('\n', 1)[1]


def xmlize(s):
    """Create XML object tree from string"""
    parser = etree.XMLParser(strip_cdata=False)
    try:
        xml = objectify.fromstring(s, parser)
    except:  ## I'm allowed because i'll re-raise it...
        print("======= CONTENT:\n%s" % s)
        print("======= END CONTENT")
        raise
    return xml


def load(filename):
    try:
        xml = objectify.parse(filename).getroot()
    except etree.XMLSyntaxError as e:
        context = 3
        file_lines = kf.get_contents(filename).split("\n")
        ctx_start = max(0, e.position[0] - context)
        ctx_stop = min(len(file_lines), e.position[0] + context)
        error_context = file_lines[ctx_start:ctx_stop]
        if ctx_start != 0:
            error_context = ["..."] + error_context
        if ctx_stop != len(file_lines):
            error_context = error_context + ["..."]
        raise SyntaxError(
            ("File %r is not valid XML:\n  %s\n  | " % (filename, e.msg)) +
            "\n  | ". join(error_context))
    except Exception as e:  ## I'm allowed because i'll re-raise it...
        print("==== CONTENT OF %r ====\n%s" \
              % (filename, kf.get_contents(filename)))
        raise
    return xml


quote_attr = quoteattr
quote_value = escape
