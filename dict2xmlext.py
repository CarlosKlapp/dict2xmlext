"""
Example file.
"""

# import array
# import enum
import xml.etree.ElementTree as ET
# import datetime as dt
# from collections import namedtuple
# import calendar
# from dateutil import tz
# from zoneinfo import ZoneInfo
from collections import deque, ChainMap
import re
from libs.abstract_baseclasses import DataProcessorAbstractBaseClass, XmlElementTypeAlias
from libs.attributes import AttributeFlags
from libs.config import Config
from libs.xml_element_wrapper_converters import convert_to_etree
# from tests.predefined_test_cases import test_case, list_of_my_classes

# Nothing to see here.
# Just a scratch file used for development and testing.

expr = re.compile('<(.*) at 0x[0-9a-f]{12}>', re.IGNORECASE)
S = '<calendar.Calendar object at 0x7ff56b9035b0>'

config = Config()
config.attr_flags = AttributeFlags.INC_ALL_DEBUG

c = ChainMap({'art': 'van gogh', 'opera': 'carmen'}, {'music': 'bach', 'art': 'rembrandt'})
d = deque('ghi')
o = object()
# e stores the element instance
# e: XmlElementTypeAlias = builder.build(list_of_my_classes)
xe: XmlElementTypeAlias = DataProcessorAbstractBaseClass.convert_to_xml(
    config=config,
    data=[c, d, o]
)

# Element instance is different every time you run the code
e: ET.Element = convert_to_etree(xe)
ET.indent(e)
print(ET.tostring(e, encoding='unicode'))
print()
