"""
Given an XML element wrapper, convert it to an XML tree.
"""
from typing import Optional
import xml.etree.ElementTree as ET
from libs.abstract_baseclasses import (
    XmlElementTypeAlias
)


def convert_to_etree(
    xml_wrapper: XmlElementTypeAlias,
    parent: Optional[ET.Element] = None
) -> ET.Element:
    """
    Convert the XML wrapper to an `xml.etree.ElementTree`.

    Args:
        xml_wrapper (XmlElementTypeAlias): An XML tree structure.
        parent (Optional[ET.Element], optional): Parent node where the XML tree will be attached. Defaults to None.

    Returns:
        ET.Element: return the root node
    """
    if parent is None:
        parent = ET.Element(xml_wrapper.tag, xml_wrapper.attributes)
    else:
        parent = ET.SubElement(parent, xml_wrapper.tag, xml_wrapper.attributes)
    parent.text = xml_wrapper.text

    for child in xml_wrapper.children:
        convert_to_etree(child, parent)

    return parent
