"""
Code to process and transform data into XML.
"""
from typing import Any, Optional, override
import xml.etree.ElementTree as ET
import datetime as dt
import re
import inspect
# import builtins
# from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.data_processor_baseclass import DataProcessorBaseClass


class DataProcessor_last_chance(DataProcessorBaseClass):
    _expr = re.compile('<(.*) at 0x[0-9a-f]{12}>', re.IGNORECASE)

    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'unknown-object'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_unknown_object_label

    def is_expected_data_type(self, data: Any) -> bool:
        return True

    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        text = str(data)
        # Objects are typically in the format '<calendar.Calendar object at 0x7ff56b9035b0>'
        # Use the regular expression to extract the object name
        if ' at 0x' in text:
            m = self._expr.match(text)
            if m is not None:
                # return 'calendar.Calendar object'
                text = m.group(1)
        return text


class DataProcessor_bool(DataProcessorBaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'bool'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_bool_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_bool(data)

    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return 'True' if data else 'False'


class DataProcessor_binary(DataProcessorBaseClass):
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'binary'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_binary_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_binary(data)

    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        codec = config.codec_binary.codec
        encoded_text, _ = codec.encode(data)
        if encoded_text.isascii():
            text = encoded_text.decode().strip()
        else:
            text = encoded_text.hex().strip()
        return text


class DataProcessor_calendar(DataProcessorBaseClass):
    '''calendar is an abstract base class.'''

    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'calendar'

    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_calendar_label

    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_calendar(data)

    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        # TODO: This isn't useful. Put here as placeholder for someone to override.
        return 'calendar object'


class DataProcessor_ChainMap(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'ChainMap'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_chainmap_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_chainmap(data)

    @override
    def recursively_process_any_nested_objects(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> None:
        config.process(parent=current, data=data.maps)


class DataProcessor_dict(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'dict'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_dict_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_dict(data)

    @override
    def recursively_process_any_nested_objects(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> None:
        for k, v in data.items():
            config.process(parent=current, data=v, child_name=str(k))


class DataProcessor_enum(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'enum'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_enum_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_enum(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data.value)


class DataProcessor_namedtuple(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'namedtuple'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_namedtuple_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_namedtuple(data)

    @override
    def get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'namedtuple'

    @override
    def recursively_process_any_nested_objects(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> None:
        for name, value in data._asdict().items():
            config.process(parent=current, data=value, child_name=name)


class DataProcessor_none(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'none'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_none_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_none(data)


class DataProcessor_numeric(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'numeric'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_numeric_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_numeric(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_sequence(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'sequence'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_sequence_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_sequence(data)

    @override
    def recursively_process_any_nested_objects(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> None:
        for v in data:
            config.process(parent=current, data=v, child_name=config.override_child_item_label)


class DataProcessor_str(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'str'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_str_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_str(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_date(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'date'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_date_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_date(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data)

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'YYYY-MM-DD'


class DataProcessor_datetime(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'datetime'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_datetime_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_datetime(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data.isoformat())

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'YYYY-MM-DDTHH:MM:SS.ffffff'  # cSpell: ignore DDTHH


class DataProcessor_time(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'time'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_time_label

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'HH:MM:SS[.ssssss]'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_time(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_timedelta(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'timedelta'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_timedelta_label

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return '[XX day[s], ]HH:MM:SS[.ssssss]'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_timedelta(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_timezone(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'timezone'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_zoneinfo_label

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'UTC±HH:MM'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_timezone(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        delta = data.utcoffset(dt.datetime.now())
        hours = delta.days * 24 + delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f'UTC+{hours:02}:{minutes:02}' if hours >= 0 else f'UTC{hours:02}:{minutes:02}'


class DataProcessor_tzinfo(DataProcessorBaseClass):
    '''tzinfo is an abstract base class.'''

    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'tzinfo'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_tzinfo_label

    @override
    def get_field_comment(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'IANA time zone database key (e.g. America/New_York, Europe/Paris or Asia/Tokyo)'

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'Zone/City'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_tzinfo(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        idx = data._filename.find('zoneinfo')
        if idx < 0:
            # not found
            text = data._filename
        else:
            # found
            text = data._filename[idx + len('zoneinfo/'):]
        return text


class DataProcessor_zoneinfo(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'zoneinfo'

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_zoneinfo_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return self.is_zoneinfo(data)

    @override
    def get_textual_representation_of_data(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> Optional[str]:
        return str(data.key)


class DataProcessor_post_processor_for_classes(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return data.__class__.__name__

    @override
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return config.override_class_label

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        # can we iterate over its values?
        # Does it have a __dict__ we iterate over?
        return hasattr(data, '__dict__') and \
            not inspect.isfunction(data) and \
            not inspect.ismethod(data)

    @override
    def recursively_process_any_nested_objects(
            self,
            config: CLASS_BUILDER_CONFIG,
            parent: ET.Element,
            current: ET.Element,
            data: Any,
            **kwargs: object
    ) -> None:
        for attr in dir(data):
            if attr.startswith("__") and attr.endswith("__"):  # skip the 'magic' objects
                continue
            attr_name = attr
            val = getattr(data, attr)
            if callable(val):  # skip methods
                continue
            config.process(parent=current, data=val, child_name=attr_name)


class DataProcessor_used_for_testing(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'DataProcessor_used_for_testing'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return True

    @override
    def get_textual_representation_of_data(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return None

    @override
    def recursively_process_any_nested_objects(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> None:
        pass

    @override
    def create_tree(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage


class DataProcessor_used_for_testing_use_hints(DataProcessorBaseClass):
    @override
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        return 'DataProcessor_used_for_testing_use_hints'

    @override
    def is_expected_data_type(self, data: Any) -> bool:
        return True

    @override
    def get_textual_representation_of_data(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return None

    @override
    def get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'test- get_field_type_hint'

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'test- get_format_string_hint'

    @override
    def create_tree(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        return None  # pragma: no coverage
