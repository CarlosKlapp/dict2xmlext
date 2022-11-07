import array
import enum
import xml.etree.ElementTree as ET
import datetime as dt
from collections import namedtuple
import calendar
from dateutil import tz
from zoneinfo import ZoneInfo
from libs.attributes import AttributeFlags
from libs.builder import Builder, BuilderConfig
from tests.predefined_test_cases import test_case, list_of_my_classes
from collections import deque, ChainMap

config = BuilderConfig()
config.attr_flags = AttributeFlags.INC_ALL_DEBUG
builder = Builder(config)

c = ChainMap({'art': 'van gogh', 'opera': 'carmen'}, {'music': 'bach', 'art': 'rembrandt'})
d = deque('ghi')
# e stores the element instance
# e: ET.Element = builder.build(list_of_my_classes)
e: ET.Element = builder.build(c)

# for i in c.items():
#     print(i)

# Element instance is different every time you run the code
ET.indent(e)
print(ET.tostring(e, encoding='unicode'))
print()
