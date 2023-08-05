#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path
import StringIO
import lxml.etree as ET

import dhtmlparser
from edeposit.amqp.aleph import marcxml

import mods_postprocessor


# Variables ===================================================================
XML_TEMPLATE = """<root>
<collection xmlns="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.loc.gov/MARC21/slim \
http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
$CONTENT
</collection>
</root>
"""


# Functions & objects =========================================================
def oai_to_xml(marc_oai):
    """
    Convert OAI to MARC XML.

    Args:
        marc_oai (str): String with either OAI or MARC XML.

    Returns:
        str: String with MARC XML.
    """
    record = marcxml.MARCXMLRecord(marc_oai)
    record.oai_marc = False

    return record.toXML()


def _add_namespace(marc_xml):
    """
    Add proper XML namespace to the `marc_xml` record.

    Args:
        marc_xml (str): String representation of the XML record.

    Returns:
        str: XML with namespace.
    """
    # return marcxml
    dom = dhtmlparser.parseString(marc_xml)
    collections = dom.find("collection")

    root = dom.find("root")
    if root:
        root[0].params = {}

    for record in dom.find("record"):
        record.params = {}

    if not collections:
        record = dom.find("record")[0]
        return XML_TEMPLATE.replace("$CONTENT", str(record))

    for col in collections:
        col.params["xmlns"] = "http://www.loc.gov/MARC21/slim"
        col.params["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        col.params["xsi:schemaLocation"] = "http://www.loc.gov/MARC21/slim " + \
                   "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"

    return str(dom)


def _read_marcxml(xml):
    """
    Read MARC XML or OAI file, convert, add namespace and return XML in
    required format with all necessities.

    Args:
        xml (str): Filename or XML string. Don't use ``\\n`` in case of
                   filename.

    Returns:
        obj: Required XML parsed with ``lxml.etree``.
    """
    # read file, if `xml` is valid file path
    marc_xml = xml
    if "\n" not in xml.strip():
        if not os.path.exists(xml):
            raise UserWarning("XML file '%s' doesn't exists!" % xml)

        with open(xml) as f:
            marc_xml = f.read()

    # process input file - convert it from possible OAI to MARC XML and add
    # required XML namespaces
    marc_xml = oai_to_xml(marc_xml)
    marc_xml = _add_namespace(marc_xml)

    file_obj = StringIO.StringIO(marc_xml)

    return ET.parse(file_obj)


def _read_template(template):
    """
    Read XSLT template.

    Args:
        template (str): Filename or XML string. Don't use ``\\n`` in case of
                        filename.

    Returns:
        obj: Required XML parsed with ``lxml.etree``.
    """
    template_xml = ""
    if "\n" in template.strip():
        template_xml = StringIO.StringIO(template)
    else:
        if not os.path.exists(template):
            raise UserWarning("Template '%s' doesn't exists!" % template)

        template_xml = open(template)

    return ET.parse(template_xml)


def transform(xml, template):
    """
    Transform `xml` using XSLT `template`.

    Args:
        xml (str): Filename or XML string. Don't use ``\\n`` in case of
                   filename.
        template (str): Filename or XML string. Don't use ``\\n`` in case of
                        filename.

    Returns:
        str: Transformed `xml` as string.
    """
    transformer = ET.XSLT(
        _read_template(template)
    )
    newdom = transformer(
        _read_marcxml(xml)
    )

    return ET.tostring(newdom, pretty_print=True, encoding="utf-8")


def transform_to_mods(marc_xml, uuid):
    """
    Convert `marc_xml` to MODS data format.

    Args:
        marc_xml (str): Filename or XML string. Don't use ``\\n`` in case of
                        filename.
        uuid (str): UUID string giving the package ID.

    Returns:
        list: Collection of transformed xml strings.
    """
    dirname = os.path.dirname(__file__)
    mods_template = os.path.join(dirname, "xslt/MARC21slim2MODS3-4-NDK.xsl")

    transformed = transform(marc_xml, mods_template)

    # return all mods tags as list
    mods = []
    dom = dhtmlparser.parseString(transformed)
    for col in dom.find("mods:mods"):
        mods.append(
            mods_postprocessor.postprocess_mods_volume(col, uuid)
        )

    return mods


# def transform_to_mods_multimonograph(marc_xml):
#     """
#     Convert `marc_xml` to multimonograph MODS data format.

#     Args:
#         marc_xml (str): Filename or XML string. Don't use ``\\n`` in case of
#                         filename.

#     Returns:
#         str: Transformed xml as string.
#     """
#     dirname = os.path.dirname(__file__)
#     mods_template = os.path.join(
#         dirname,
#         "xslt/MARC21toMultiMonographTitle.xsl"
#     )

#     return transform(marc_xml, mods_template)


# def transform_to_mods_periodical(marc_xml):
#     """
#     Convert `marc_xml` to periodical MODS data format.

#     Args:
#         marc_xml (str): Filename or XML string. Don't use ``\\n`` in case of
#                         filename.

#     Returns:
#         str: Transformed xml as string.
#     """
#     dirname = os.path.dirname(__file__)
#     mods_template = os.path.join(
#         dirname,
#         "xslt/MARC21toPeriodicalTitle.xsl"
#     )

#     return transform(marc_xml, mods_template)
