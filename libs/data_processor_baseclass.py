from abc import abstractmethod
import array
import enum
from typing import Any, Callable, Dict, List, Optional, TypeAlias, cast, Final, final
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from collections.abc import Sized
from dataclasses import dataclass, field
import datetime as dt
import numbers
import time
import calendar
import uuid
import sys
from collections import ChainMap, deque, namedtuple
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE


class DataProcessor_BaseClass:
    """
    [<class 'datetime.timezone'>, <class 'datetime.tzinfo'>, <class 'object'>]
    [<class 'dateutil.tz.tz.tzfile'>, <class 'dateutil.tz._common._tzinfo'>, <class 'datetime.tzinfo'>, <class 'object'>]
    [<class 'zoneinfo.ZoneInfo'>, <class 'datetime.tzinfo'>, <class 'object'>]
    """

    # Used by child classes
    _custom_element_name: Optional[str] = None

    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return None

    def get_field_comment(self, data: Any, **kwargs) -> Optional[str]:
        return None

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return None

    @abstractmethod
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        pass  # pragma: no cover

    def process(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        e = self.create_tree(config=config, parent=parent, data=data, child_name=child_name)
        if (e is None):
            return None
        self.add_attributes(config=config, parent=parent, current=e, data=data)
        return e

    def attr_alt_id(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_ALT_ID
        key: Final[str] = AttributeFlagsNames[attrflag]
        return {key: str(uuid.uuid4())}

    def attr_binary_encoding(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_BINARY_ENCODING
        return {AttributeFlagsNames[attrflag]: config.codec_binary.codec.name}

    def attr_debug_info(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_DEBUG_INFO
        return {AttributeFlagsNames[attrflag]: f'processed_by:{self.__class__.__name__}'}

    def attr_field_comment(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_COMMENT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_field_comment(data, **kwargs)
        if (hint is not None):
            attr[key] = hint
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
        return {AttributeFlagsNames[attrflag]: str(len(data))}

    def attr_python_data_type(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_PYTHON_DATA_TYPE
        # type has the form "<class 'int'>". Use [1:-1] to convert it to "class 'int'"
        return {AttributeFlagsNames[attrflag]: str(type(data))[1:-1]}

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
        return {AttributeFlagsNames[attrflag]: 'anyType'}

    def add_attributes(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        attr: Dict[str, str] = {}

        if ((AttributeFlags.INC_BINARY_ENCODING & config.attr_flags) and self.is_binary(data)):
            a = self.attr_binary_encoding(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if (AttributeFlags.INC_DEBUG_INFO & config.attr_flags):
            a = self.attr_debug_info(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if ((AttributeFlags.INC_FIELD_COMMENT & config.attr_flags) and self.get_field_comment(data, **kwargs) is not None):
            a = self.attr_field_comment(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if ((AttributeFlags.INC_FIELD_TYPE_HINT & config.attr_flags) and self.get_field_type_hint(data, **kwargs) is not None):
            a = self.attr_field_type_hint(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if ((AttributeFlags.INC_FORMAT_STRING_HINT & config.attr_flags) and self.get_format_string_hint(data, **kwargs) is not None):
            a = self.attr_format_string_hint(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if (AttributeFlags.INC_LEN & config.attr_flags) and (isinstance(data, Sized)):
            a = self.attr_len(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if (AttributeFlags.INC_PYTHON_DATA_TYPE & config.attr_flags):
            a = self.attr_python_data_type(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        # Don't process AttributeFlags.INC_SEQ_ID here. It is processed and added when the Element is created.

        if (AttributeFlags.INC_SIZE_BYTES & config.attr_flags):
            a = self.attr_size_bytes(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        if (AttributeFlags.INC_XSD_DATA_TYPE & config.attr_flags):
            a = self.attr_xsd_data_type(config=config, parent=parent, current=current, data=data, **kwargs)
            attr |= a

        current.attrib.update(attr)

    @ final
    @ staticmethod
    def is_bytes(data: Any) -> bool:
        return isinstance(data, bytes)

    @ final
    @ staticmethod
    def is_bytearray(data: Any) -> bool:
        return isinstance(data, bytearray)

    @ final
    @ staticmethod
    def is_binary(data: Any) -> bool:
        return DataProcessor_BaseClass.is_bytes(data) or DataProcessor_BaseClass.is_bytearray(data)

    @ final
    @ staticmethod
    def is_bool(data: Any) -> bool:
        return isinstance(data, bool) and str(type(data)) == "<class 'bool'>"

    @ final
    @ staticmethod
    def is_calendar(data: Any) -> bool:
        return isinstance(data, calendar.Calendar)

    @ final
    @ staticmethod
    def is_ChainMap(data: Any) -> bool:
        return isinstance(data, ChainMap)

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
    def is_dict(data: Any) -> bool:
        return isinstance(data, dict)

    @ final
    @ staticmethod
    def is_enum(data: Any) -> bool:
        return isinstance(data, enum.Enum)

    @ final
    @ staticmethod
    def is_namedtuple(data: Any) -> bool:
        return isinstance(data, tuple) and hasattr(data, '_asdict') and hasattr(data, '_fields')

    @ final
    @ staticmethod
    def is_none(data: Any) -> bool:
        return (data is None)

    @ final
    @ staticmethod
    def is_numeric(data: Any) -> bool:
        return isinstance(data, numbers.Number) and (not isinstance(data, enum.Enum)) and str(type(data)) != "<class 'bool'>"

    @ final
    @ staticmethod
    def is_sequence(data: Any) -> bool:
        return isinstance(data, list | tuple | set | range | array.array | deque) and not DataProcessor_BaseClass.is_namedtuple(data)

    @ final
    @ staticmethod
    def is_str(data: Any) -> bool:
        return isinstance(data, str)

    @ final
    @ staticmethod
    def is_time(data: Any) -> bool:
        return isinstance(data, dt.time)

    @ final
    @ staticmethod
    def is_timedelta(data: Any) -> bool:
        return isinstance(data, dt.timedelta)

    @ final
    @ staticmethod
    def is_timezone(data: Any) -> bool:
        return isinstance(data, dt.timezone)

    @ final
    @ staticmethod
    def is_zoneinfo(data: Any) -> bool:
        return isinstance(data, ZoneInfo)

    @ final
    @ staticmethod
    def is_tzinfo(data: Any) -> bool:
        return isinstance(data, dt.tzinfo) and not DataProcessor_BaseClass.is_timezone(data) and not DataProcessor_BaseClass.is_zoneinfo(data)
