# from abc import abstractmethod
from abc import abstractmethod
import array
import codecs
from ctypes import Array
# from codecs import Codec
import enum
from tokenize import Number
from typing import Any, Callable, Dict, List, Optional, TypeAlias, cast, Final, final
import xml.etree.ElementTree as ET
# from xml.etree.ElementTree import Element, SubElement
from collections.abc import Sized
from dataclasses import dataclass, field
import datetime as dt
import numbers
import time
import calendar
import uuid
import sys

CLASS_BUILDER_CONFIG: TypeAlias = "BuilderConfig"
CLASS_DATA_PROCESSOR: TypeAlias = "DataProcessor"
PROCESSOR_RETURN_TYPE: TypeAlias = Optional[ET.Element]
PROCESSOR_FUNC_TYPE: TypeAlias = Callable[[CLASS_BUILDER_CONFIG, ET.Element, Any], PROCESSOR_RETURN_TYPE]


class AttributeFlags(enum.Flag):
    NONE = 0
    INC_ALT_ID = enum.auto()
    INC_BINARY_ENCODING = enum.auto()
    INC_FIELD_TYPE_HINT = enum.auto()
    INC_FORMAT_STRING_HINT = enum.auto()
    INC_LEN = enum.auto()
    INC_PYTHON_DATA_TYPE = enum.auto()
    INC_SEQ_ID = enum.auto()
    INC_SIZE_BYTES = enum.auto()
    INC_XSD_DATA_TYPE = enum.auto()  # not implemented
    INC_ALL = INC_BINARY_ENCODING | INC_FIELD_TYPE_HINT | INC_FORMAT_STRING_HINT | INC_LEN | \
        INC_PYTHON_DATA_TYPE | INC_SEQ_ID | INC_SIZE_BYTES | INC_XSD_DATA_TYPE


AttributeFlagsNames: Dict[AttributeFlags, str] = {
    AttributeFlags.INC_ALT_ID: "alt_id",
    AttributeFlags.INC_BINARY_ENCODING: "binary_encoding",
    AttributeFlags.INC_FIELD_TYPE_HINT: "type_hint",
    AttributeFlags.INC_FORMAT_STRING_HINT: "format_string_hint",
    AttributeFlags.INC_LEN: "length",
    AttributeFlags.INC_PYTHON_DATA_TYPE: "py_type",
    AttributeFlags.INC_SEQ_ID: "id",
    AttributeFlags.INC_SIZE_BYTES: "size_bytes",
    AttributeFlags.INC_XSD_DATA_TYPE: "xsd_type",
}


class DataProcessor:
    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return None

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return None

    @abstractmethod
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        pass

    def process(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        e = self.create_tree(config=config, parent=parent, data=data, child_name=child_name)
        if (e is None):
            return None

        self.add_attributes(config=config, parent=parent, current=e, data=data)
        return e

    def attr_alt_id(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_ALT_ID
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        attr[key] = str(uuid.uuid4())
        return attr

    def attr_binary_encoding(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_BINARY_ENCODING
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        attr[key] = config.codec_binary.codec.name
        return attr

    def attr_field_type_hint(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_TYPE_HINT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_field_type_hint(data, **kwargs)
        if (hint is not None):
            attr[key] = hint
        return attr

    def attr_format_string_hint(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FORMAT_STRING_HINT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_format_string_hint(data, **kwargs)
        if (hint is not None):
            attr[key] = hint
        return attr

    def attr_len(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_LEN
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        attr[key] = str(len(data))
        return attr

    def attr_python_data_type(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_PYTHON_DATA_TYPE
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        attr[key] = str(type(data))
        return attr

    def attr_size_bytes(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_SIZE_BYTES
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        size = sys.getsizeof(data, -1)
        if (size > 0):
            attr[key] = str(size)
        return attr

    def attr_xsd_data_type(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_XSD_DATA_TYPE
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        attr[key] = 'anyType'
        return attr

    def add_attributes(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        attr: Dict[str, str] = {}

        if ((AttributeFlags.INC_BINARY_ENCODING & config.attr_flags) and self.is_binary(data)):
            a = self.attr_binary_encoding(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        if ((AttributeFlags.INC_FIELD_TYPE_HINT & config.attr_flags) and self.get_field_type_hint(data, **kwargs) is not None):
            a = self.attr_field_type_hint(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        if ((AttributeFlags.INC_FORMAT_STRING_HINT & config.attr_flags) and self.get_format_string_hint(data, **kwargs) is not None):
            a = self.attr_format_string_hint(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        if (AttributeFlags.INC_LEN & config.attr_flags) and (isinstance(data, Sized)):
            a = self.attr_len(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        if (AttributeFlags.INC_PYTHON_DATA_TYPE & config.attr_flags):
            a = self.attr_python_data_type(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        # Don't process AttributeFlags.INC_SEQ_ID here. It is processed and added when the Element is created.

        if (AttributeFlags.INC_SIZE_BYTES & config.attr_flags):
            a = self.attr_size_bytes(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        if (AttributeFlags.INC_XSD_DATA_TYPE & config.attr_flags):
            a = self.attr_xsd_data_type(config=config, parent=parent, current=current, data=data, **kwargs)
            attr.update(a)

        current.attrib.update(attr)

    @ final
    @ staticmethod
    def is_enum(data: Any) -> bool:
        return isinstance(data, enum.Enum)

    @ final
    @ staticmethod
    def is_bytes(data: Any) -> bool:
        return isinstance(data, bytes | bytearray)

    @ final
    @ staticmethod
    def is_binary(data: Any) -> bool:
        return DataProcessor.is_bytes(data)

    @ final
    @ staticmethod
    def is_sequence(data: Any) -> bool:
        return isinstance(data, list | tuple | set | range | Array)

    @ final
    @ staticmethod
    def is_str(data: Any) -> bool:
        return isinstance(data, str)

    @ final
    @ staticmethod
    def is_numeric(data: Any) -> bool:
        return isinstance(data, numbers.Number) and (not isinstance(data, enum.Enum))

    @ final
    @ staticmethod
    def is_dict(data: Any) -> bool:
        return isinstance(data, dict)

    @ final
    @ staticmethod
    def is_timedelta(data: Any) -> bool:
        return isinstance(data, dt.timedelta)

    @ final
    @ staticmethod
    def is_tzinfo(data: Any) -> bool:
        return isinstance(data, dt.tzinfo) and not isinstance(data, dt.timezone)

    @ final
    @ staticmethod
    def is_timezone(data: Any) -> bool:
        return isinstance(data, dt.timezone)

    @ final
    @ staticmethod
    def is_time(data: Any) -> bool:
        return isinstance(data, dt.time)

    @ final
    @ staticmethod
    def is_date(data: Any) -> bool:
        return isinstance(data, dt.date) and not isinstance(data, dt.datetime)

    @ final
    @ staticmethod
    def is_datetime(data: Any) -> bool:
        return isinstance(data, dt.datetime)

    @ final
    @ staticmethod
    def is_calendar(data: Any) -> bool:
        return isinstance(data, calendar.Calendar)

    @ final
    @ staticmethod
    def is_none(data: Any) -> bool:
        return (data is None)


class DataProcessor_last_chance(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_none(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_none(data):
            new_tag: str = config.get_default_item_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            return current
        else:
            return None


class DataProcessor_enum(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_enum(data):
            new_tag: str = config.get_default_item_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data.value)
            return current
        else:
            return None


class DataProcessor_str(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_str(data):
            new_tag: str = config.get_default_item_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class DataProcessor_bytes(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_bytes(data):
            new_tag: str = config.get_default_item_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            codec = config.codec_binary.codec
            text, _ = codec.encode(cast(str, data), errors=config.codec_binary.codec_error_handler)
            current.text = cast(str, text)
            return current
        else:
            return None


class DataProcessor_numeric(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_numeric(data):
            new_tag: str = config.get_default_item_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class DataProcessor_dict(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_dict(data):
            new_tag: str = config.get_default_dict_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            for k, v in data.items():
                child = config.process(parent=current, data=v, child_name=str(k))
            return current
        else:
            return None


class DataProcessor_sequences(DataProcessor):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_sequence(data):
            new_tag: str = config.get_default_sequence_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            for v in data:
                child = config.process(parent=current, data=v, child_name=config.default_item_name)
            return current
        else:
            return None


class DataProcessor_timedelta(DataProcessor):
    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'XX days, HH:MM:SS.ssssss'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_timedelta(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class DataProcessor_timezone(DataProcessor):
    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'datetime.timezone(datetime.timedelta(days=-1, seconds=64800), ''tz name'')'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_timezone(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(repr(data))
            return current
        else:
            return None


class DataProcessor_time(DataProcessor):
    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'HH:MM:SS.ssssss'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_time(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class DataProcessor_date(DataProcessor):
    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DD'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_date(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class DataProcessor_datetime(DataProcessor):
    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DDTHH:MM:SS.ffffff'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_datetime(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data.isoformat())
            return current
        else:
            return None


class DataProcessor_tzinfo(DataProcessor):
    '''tzinfo is an abstract base class.'''

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_tzinfo(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(repr(data))
            return current
        else:
            return None


class DataProcessor_calendar(DataProcessor):
    '''calendar is an abstract base class.'''

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        if self.is_calendar(data):
            new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name)
            current = config.SubElement(parent, new_tag)
            current.text = str(data)
            return current
        else:
            return None


class CodecWrapper:
    _codecinfo: Optional[codecs.CodecInfo] = None
    codec_error_handler: str = 'surrogatepass'
    ''' see https://docs.python.org/3/library/codecs.html#codec-base-classes for valid values'''
    _codec_name: str = 'utf-8'

    @ property
    def codec_name(self) -> str:
        return self._codec_name

    @ codec_name.setter
    def codec_name(self, codec_name: str) -> None:
        self._codec_name = codec_name

    @ property
    def codec(self) -> codecs.CodecInfo:
        if (self._codecinfo is None):
            self._codecinfo = codecs.lookup(self._codec_name)
        else:
            assert self._codecinfo.name is not None
            if (self._codecinfo.name.lower() != self._codec_name.lower()):
                self._codecinfo = codecs.lookup(self._codec_name)

        self._codec_name = self._codecinfo.name
        return self._codecinfo

    @ codec.setter
    def codec(self, codecinfo: codecs.CodecInfo) -> None:
        self._codec_name = codecinfo.name
        self._codecinfo = codecinfo


@ dataclass
class BuilderConfig:
    default_processors: List[DataProcessor] = field(default_factory=lambda: [
        DataProcessor_bytes(),
        DataProcessor_calendar(),
        DataProcessor_date(),
        DataProcessor_datetime(),
        DataProcessor_dict(),
        DataProcessor_enum(),
        DataProcessor_none(),
        DataProcessor_numeric(),
        DataProcessor_sequences(),
        DataProcessor_str(),
        DataProcessor_time(),
        DataProcessor_timedelta(),
        DataProcessor_timezone(),
        DataProcessor_tzinfo(),
    ])
    custom_processors: List[DataProcessor] = field(default_factory=list)
    last_chance_processor: DataProcessor_last_chance = DataProcessor_last_chance()
    root_name: str = 'root'
    default_dict_name: str = 'dict'
    default_sequence_name: str = 'sequence'
    default_item_name: str = 'item'
    default_name: str = 'unknown_object'
    codec_binary: CodecWrapper = CodecWrapper()
    codec_text: CodecWrapper = CodecWrapper()
    num_elements_counter: int = 0
    attr_flags: AttributeFlags = AttributeFlags.NONE
    attr_flag_names: Dict[AttributeFlags, str] = field(default_factory=lambda: AttributeFlagsNames)

    def __post_init__(self) -> None:
        self.codec_binary.codec_name = 'base64'

    def _process_helper(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        for processor in self.custom_processors:
            e = processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
            if (e is not None):
                return e

        for processor in self.default_processors:
            e = processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
            if (e is not None):
                return e

        e = self.last_chance_processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
        return e

    def process(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> PROCESSOR_RETURN_TYPE:
        e = self._process_helper(parent=parent, data=data, child_name=child_name)
        assert e is not None

    def get_default_dict_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        return self.default_dict_name if child_name is None else child_name

    def get_default_sequence_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        return self.default_sequence_name if child_name is None else child_name

    def get_default_item_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        return self.default_item_name if child_name is None else child_name

    def get_default_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        return self.default_name if child_name is None else child_name

    def include_seq_id_as_attribute(self) -> Dict[str, str]:
        attrib: Dict[str, str] = {}
        if (AttributeFlags.INC_SEQ_ID & config.attr_flags):
            attrflag: Final[AttributeFlags] = AttributeFlags.INC_SEQ_ID
            key: Final[str] = AttributeFlagsNames[attrflag]
            attrib[key] = str(config.num_elements_counter)
        return attrib

    def Element(self, tag: str, attrib: Dict[str, str] = {}, **kwargs) -> ET.Element:
        self.num_elements_counter += 1
        extra = self.include_seq_id_as_attribute()
        extra.update(attrib)
        # Don't pass kwargs to Element, they will just get added as attrbiutes
        e = ET.Element(tag, attrib=extra)
        return e

    def SubElement(self, parent: ET.Element, tag: str, attrib: Dict[str, str] = {}, **kwargs) -> ET.Element:
        self.num_elements_counter += 1
        extra = self.include_seq_id_as_attribute()
        extra.update(attrib)
        # Don't pass kwargs to Element, they will just get added as attrbiutes
        e = ET.SubElement(parent, tag, attrib=extra)
        return e


class Builder:
    config: BuilderConfig

    def __init__(self, config: BuilderConfig) -> None:
        self.config = config

    def build(self, data: Any, attrib: Dict[str, str] = {}, **kwargs) -> ET.Element:
        self.config.num_elements_counter = 0
        root: ET.Element = self.config.Element(tag=self.config.root_name, attrib=attrib, **kwargs)
        self.config.process(parent=root, data=data, **kwargs)
        return root


class Color(enum.Enum):
    RED = 1
    GREEN = "green"


class Shape(enum.IntEnum):
    CIRCLE = 1


class Perm(enum.IntFlag):
    R = 4


class Food(enum.Flag):
    FISH = enum.auto()
    VEGGIE = "veggie"


# Driver Program
s = {
    12: 144,
    'none-nothing': None,
    'empty-string': '',
    'Shape': Shape.CIRCLE,
    'Perm': Perm.R,
    'name': 'geeksforgeeks',
    'city': 'new york',
    'sub': {
        'sub1': 'v1',
        'sub2': 'v2',
        'l1': ['a', 'b', 'c'],
        'dt': {
            'my timezone': dt.timezone(dt.timedelta(hours=-6), 'test'),
            'my date': dt.date(2022, 11, 12),
            'my datetime': dt.datetime(2022, 11, 12, 14, 12, 5, 78),
            'my time': dt.time(16, 15, 14),
            'my timedelta': dt.timedelta(days=34, hours=13, minutes=46, seconds=57, milliseconds=675, microseconds=423),
        },
        'Color-R': Color.RED,
        'Color-G': Color.GREEN,
        'Food-F': Food.FISH,
        'Food-V': Food.VEGGIE
    },
    'stock': 920


}

config = BuilderConfig()
# config.attr_flags = AttributeFlags.NONE
config.attr_flags = AttributeFlags.INC_ALL
builder = Builder(config)


# e stores the element instance
# e = dict_to_xml('company', s)
e: ET.Element = builder.build(s)

# Element instance is different
# every time you run the code
# print(tostring(e))
ET.indent(e)
# ET.dump(e)
print(ET.tostring(e, encoding='unicode'))

# etree = ET.ElementTree(e)
# print(repr(etree))
