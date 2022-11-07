from abc import abstractmethod
# from codecs import Codec
import enum
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
import inspect
# import builtins
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.data_processor_baseclass import DataProcessor_BaseClass

debug_break_on_DataProcessor: Final[bool] = True


class DataProcessor_last_chance(DataProcessor_BaseClass):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()
        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_bool(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'bool'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_bool(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)

        current.text = 'True' if data else 'False'
        return current


class DataProcessor_binary(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'binary'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_binary(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        codec = config.codec_binary.codec
        encoded_text, _ = codec.encode(data)
        if encoded_text.isascii():
            text = encoded_text.decode().strip()
        else:
            text = encoded_text.hex().strip()
        current.text = text
        return current


class DataProcessor_calendar(DataProcessor_BaseClass):
    '''calendar is an abstract base class.'''

    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'calendar'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_calendar(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_ChainMap(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'ChainMap'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_ChainMap(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_ChainMap_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        child = config.process(parent=current, data=data.maps, child_name=child_name)
        return current


class DataProcessor_dict(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'dict'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_dict(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_dict_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        for k, v in data.items():
            child = config.process(parent=current, data=v, child_name=str(k))
        return current


class DataProcessor_enum(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'enum'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_enum(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data.value)
        return current


class DataProcessor_namedtuple(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'namedtuple'

    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'namedtuple'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_namedtuple(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_namedtuple_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        for name, value in data._asdict().items():
            child = config.process(parent=current, data=value, child_name=name)
        return current


class DataProcessor_none(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'none'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        # sourcery skip: inline-immediately-returned-variable
        if not self.is_none(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        return current


class DataProcessor_numeric(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'numeric'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_numeric(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_sequences(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'sequences'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_sequence(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_sequence_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        item_name: str = config.get_default_item_name(parent=parent, data=data)
        for v in data:
            child = config.process(parent=current, data=v, child_name=item_name)
        return current


class DataProcessor_str(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'str'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_str(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_date(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'date'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DD'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_date(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_datetime(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'datetime'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DDTHH:MM:SS.ffffff'  # cSpell: ignore DDTHH

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_datetime(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data.isoformat())
        return current


class DataProcessor_time(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'time'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'HH:MM:SS[.ssssss]'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_time(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_timedelta(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'timedelta'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return '[XX day[s], ]HH:MM:SS[.ssssss]'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_timedelta(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data)
        return current


class DataProcessor_timezone(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'timezone'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'UTC±HH:MM'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_timezone(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        delta = data.utcoffset(dt.datetime.now())
        hours = delta.days * 24 + delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        current.text = f'UTC+{hours:02}:{minutes:02}' if hours >= 0 else f'UTC{hours:02}:{minutes:02}'
        return current


class DataProcessor_tzinfo(DataProcessor_BaseClass):
    '''tzinfo is an abstract base class.'''

    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'tzinfo'

    def get_field_comment(self, data: Any, **kwargs) -> Optional[str]:
        return 'IANA time zone database key (e.g. America/New_York, Europe/Paris or Asia/Tokyo)'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'Zone/City'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_tzinfo(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        idx = data._filename.find('zoneinfo')
        if idx < 0:
            # not found
            current.text = data._filename
        else:
            # found
            current.text = data._filename[idx + len('zoneinfo/'):]
        return current


class DataProcessor_zoneinfo(DataProcessor_BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._custom_element_name = 'zoneinfo'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_zoneinfo(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = config.get_default_name(parent=parent, data=data, child_name=child_name or self._custom_element_name)
        current = config.SubElement(parent, new_tag)
        current.text = str(data.key)
        return current


class DataProcessor_class_custom_post_processor(DataProcessor_BaseClass):
    def is_PythonClass(self, data: Any) -> bool:
        # can we iterate over its values
        return hasattr(data, '__dict__') and not inspect.isfunction(data) and not inspect.ismethod(data)

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_PythonClass(data):
            return None
        if __debug__ and debug_break_on_DataProcessor:
            breakpoint()

        new_tag: str = data.__class__.__name__
        current = config.SubElement(parent, new_tag)
        for attr in dir(data):
            if attr.startswith("__") and attr.endswith("__"):  # skip the 'magic' objects
                continue
            attr_name = attr
            val = getattr(data, attr)
            if callable(val):  # skip methods
                continue
            child = config.process(parent=current, data=val, child_name=attr_name)
        return current


class DataProcessor_used_for_testing(DataProcessor_BaseClass):
    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage


class DataProcessor_used_for_testing_use_hints(DataProcessor_BaseClass):
    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'test- get_field_type_hint'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'test- get_format_string_hint'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage
