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
import re
import inspect
# import builtins
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.data_processor_baseclass import DataProcessor_BaseClass


class DataProcessor_last_chance(DataProcessor_BaseClass):
    _expr = re.compile('<(.*) at 0x[0-9a-f]{12}>', re.IGNORECASE)

    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'unknown-object'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_unknown_object_label

    def is_expected_data_type(self, data: Any) -> bool:
        return True

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        text = str(data)
        # Objects are typically in the format '<calendar.Calendar object at 0x7ff56b9035b0>'
        # Use the regular expression to extract the object name
        if ' at 0x' in text:
            m = self._expr.match(text)
            if m is not None:
                # return 'calendar.Calendar object'
                text = m.group(1)
        return text


class DataProcessor_bool(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'bool'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_bool_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_bool(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return 'True' if data else 'False'


class DataProcessor_binary(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'binary'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_binary_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_binary(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        codec = config.codec_binary.codec
        encoded_text, _ = codec.encode(data)
        if encoded_text.isascii():
            text = encoded_text.decode().strip()
        else:
            text = encoded_text.hex().strip()
        return text


class DataProcessor_calendar(DataProcessor_BaseClass):
    '''calendar is an abstract base class.'''

    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'calendar'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_calendar_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_calendar(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        # TODO: This isn't useful. Put here as placeholder for someone to override.
        return 'calendar object'


class DataProcessor_ChainMap(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'ChainMap'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_ChainMap_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_ChainMap(data)

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        child = config.process(parent=current, data=data.maps)


class DataProcessor_dict(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'dict'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_dict_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_dict(data)

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        for k, v in data.items():
            child = config.process(parent=current, data=v, child_name=str(k))


class DataProcessor_enum(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'enum'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_enum_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_enum(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data.value)


class DataProcessor_namedtuple(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'namedtuple'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_namedtuple_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_namedtuple(data)

    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'namedtuple'

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        for name, value in data._asdict().items():
            child = config.process(parent=current, data=value, child_name=name)


class DataProcessor_none(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'none'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_none_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_none(data)


class DataProcessor_numeric(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'numeric'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_numeric_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_numeric(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data)


class DataProcessor_sequence(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'sequence'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_sequence_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_sequence(data)

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        for v in data:
            child = config.process(parent=current, data=v, child_name=config.override_child_item_label)


class DataProcessor_str(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'str'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_str_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_str(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data)


class DataProcessor_date(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'date'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_date_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_date(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data)

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DD'


class DataProcessor_datetime(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'datetime'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_datetime_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_datetime(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data.isoformat())

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'YYYY-MM-DDTHH:MM:SS.ffffff'  # cSpell: ignore DDTHH


class DataProcessor_time(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'time'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_time_label

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'HH:MM:SS[.ssssss]'

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_time(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data)


class DataProcessor_timedelta(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'timedelta'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_timedelta_label

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return '[XX day[s], ]HH:MM:SS[.ssssss]'

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_timedelta(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data)


class DataProcessor_timezone(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'timezone'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_zoneinfo_label

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'UTC±HH:MM'

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_timezone(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        delta = data.utcoffset(dt.datetime.now())
        hours = delta.days * 24 + delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f'UTC+{hours:02}:{minutes:02}' if hours >= 0 else f'UTC{hours:02}:{minutes:02}'


class DataProcessor_tzinfo(DataProcessor_BaseClass):
    '''tzinfo is an abstract base class.'''

    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'tzinfo'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_tzinfo_label

    def get_field_comment(self, data: Any, **kwargs) -> Optional[str]:
        return 'IANA time zone database key (e.g. America/New_York, Europe/Paris or Asia/Tokyo)'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'Zone/City'

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_tzinfo(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        idx = data._filename.find('zoneinfo')
        if idx < 0:
            # not found
            text = data._filename
        else:
            # found
            text = data._filename[idx + len('zoneinfo/'):]
        return text


class DataProcessor_zoneinfo(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'zoneinfo'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_zoneinfo_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_zoneinfo(data)

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return str(data.key)


class DataProcessor_post_processor_for_classes(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return data.__class__.__name__

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_class_label

    def is_expected_data_type(self, data: Any) -> bool:
        # can we iterate over its values?
        # Does it have a __dict__ we iterate over?
        return hasattr(data, '__dict__') and not inspect.isfunction(data) and not inspect.ismethod(data)

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        for attr in dir(data):
            if attr.startswith("__") and attr.endswith("__"):  # skip the 'magic' objects
                continue
            attr_name = attr
            val = getattr(data, attr)
            if callable(val):  # skip methods
                continue
            child = config.process(parent=current, data=val, child_name=attr_name)


class DataProcessor_used_for_testing(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'DataProcessor_used_for_testing'

    def is_expected_data_type(self, data: Any) -> bool:
        return True

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return None

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        pass

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage


class DataProcessor_used_for_testing_use_hints(DataProcessor_BaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'DataProcessor_used_for_testing_use_hints'

    def is_expected_data_type(self, data: Any) -> bool:
        return True

    def get_textual_representation_of_data(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> Optional[str]:
        return None

    def recursively_process_any_nested_objects(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, current: ET.Element, data: Any, **kwargs) -> None:
        pass

    def get_field_type_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'test- get_field_type_hint'

    def get_format_string_hint(self, data: Any, **kwargs) -> Optional[str]:
        return 'test- get_format_string_hint'

    def create_tree(self, config: CLASS_BUILDER_CONFIG, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage
