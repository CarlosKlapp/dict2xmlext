"""
Code to process and transform data into XML.
"""
# pylint: disable=C0103; invalid-name
from typing import Any, Final, Optional, override
import datetime as dt
import re
import inspect
import os
from pathlib import Path
from libs.abstract_baseclasses import (
    DataProcessorAbstractBaseClass,
    DataProcessorReturnTypeAlias,
    XmlElementTypeAlias
)
from libs.misc import convert_windows_tz_name_to_iani_name


class DataProcessor_last_chance(DataProcessorAbstractBaseClass):
    """
    This is the final chance to encode the data. No other data processor was able to
    encode the data. Use this encoder.
    """

    _REGEX_OBJECT: Final[re.Pattern[str]] = re.compile(r'<(.*) at 0x[0-9a-f]+>', re.IGNORECASE)

    def _get_default_element_name(self, data: Any) -> str:
        return 'unknown-object'

    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_unknown_object_label

    def _is_expected_data_type(self, data: Any) -> bool:
        return True

    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        text = str(data)
        # Objects are typically in the format '<calendar.Calendar object at 0x7ff56b9035b0>'
        # Use the regular expression to extract the object name
        if ' at 0x' in text:
            m = self._REGEX_OBJECT.match(text)
            if m is not None:
                # return 'calendar.Calendar object'
                text = m.group(1)
        return text


class DataProcessor_bool(DataProcessorAbstractBaseClass):
    """
    Encode boolean values.
    """

    def _get_default_element_name(self, data: Any) -> str:
        return 'bool'

    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_bool_label

    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_bool(data)

    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return 'True' if data else 'False'


class DataProcessor_binary(DataProcessorAbstractBaseClass):
    """
    Encode binary values.
    """

    def _get_default_element_name(self, data: Any) -> str:
        return 'binary'

    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_binary_label

    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_binary(data)

    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        codec = self.config.codec_binary.codec
        encoded_text, _ = codec.encode(data)
        if encoded_text.isascii():
            text = encoded_text.decode().strip()
        else:
            text = encoded_text.hex().strip()
        return text


class DataProcessor_calendar(DataProcessorAbstractBaseClass):
    """
    Encode a calendar value.

    calendar is an abstract base class.
    """

    def _get_default_element_name(self, data: Any) -> str:
        return 'calendar'

    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_calendar_label

    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_calendar(data)

    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        # TODO: This isn't a useful value. Put here as placeholder for someone to override.
        return 'calendar object'


class DataProcessor_ChainMap(DataProcessorAbstractBaseClass):
    """
    Encode a ChainMap value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'ChainMap'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_chainmap_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_chainmap(data)

    @override
    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        self._process(
            config=self.config,
            parent=current,
            data=data.maps,
            child_name=None
        )


class DataProcessor_dict(DataProcessorAbstractBaseClass):
    """
    Encode a dict value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'dict'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_dict_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_dict(data)

    @override
    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        for k, v in data.items():
            self._process(
                config=self.config,
                parent=current,
                data=v,
                child_name=str(k)
            )


class DataProcessor_enum(DataProcessorAbstractBaseClass):
    """
    Encode an enum value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'enum'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_enum_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_enum(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data.value)


class DataProcessor_namedtuple(DataProcessorAbstractBaseClass):
    """
    Encode a named tuple value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'namedtuple'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_namedtuple_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_namedtuple(data)

    @override
    def _get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'namedtuple'

    @override
    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        for name, value in data._asdict().items():
            self._process(
                config=self.config,
                parent=current,
                data=value,
                child_name=name
            )


class DataProcessor_none(DataProcessorAbstractBaseClass):
    """
    Encode a None value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'none'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_none_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_none(data)


class DataProcessor_numeric(DataProcessorAbstractBaseClass):
    """
    Encode a numeric value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'numeric'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_numeric_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_numeric(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_sequence(DataProcessorAbstractBaseClass):
    """
    Encode a sequence value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'sequence'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_sequence_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_sequence(data)

    @override
    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        for v in data:
            self._process(
                config=self.config,
                parent=current,
                data=v,
                child_name=self.config.override_child_item_label
            )


class DataProcessor_str(DataProcessorAbstractBaseClass):
    """
    Encode a str value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'str'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_str_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_str(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_date(DataProcessorAbstractBaseClass):
    """
    Encode a date value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'date'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_date_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_date(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data)

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'YYYY-MM-DD'


class DataProcessor_datetime(DataProcessorAbstractBaseClass):
    """
    Encode a datetime value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'datetime'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_datetime_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_datetime(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data.isoformat())

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'YYYY-MM-DDTHH:MM:SS.ffffff'  # cSpell: ignore DDTHH


class DataProcessor_time(DataProcessorAbstractBaseClass):
    """
    Encode a time value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'time'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_time_label

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'HH:MM:SS[.ssssss]'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_time(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_timedelta(DataProcessorAbstractBaseClass):
    """
    Encode a timedelta value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'timedelta'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_timedelta_label

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return '[XX day[s], ]HH:MM:SS[.ssssss]'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_timedelta(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data)


class DataProcessor_timezone(DataProcessorAbstractBaseClass):
    """
    Encode a timezone value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'timezone'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_zoneinfo_label

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'UTC±HH:MM'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_timezone(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        delta = data.utcoffset(dt.datetime.now())
        hours = delta.days * 24 + delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f'UTC+{hours:02}:{minutes:02}' if hours >= 0 else f'UTC{hours:02}:{minutes:02}'


class DataProcessor_tzinfo(DataProcessorAbstractBaseClass):
    """
    Encode a tzinfo value.

    tzinfo is an abstract base class.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'tzinfo'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_tzinfo_label

    @override
    def _get_field_comment(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'IANA time zone database key (e.g. America/New_York, Europe/Paris or Asia/Tokyo)'

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'Zone/City'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_tzinfo(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        text: str = 'unknown'
        if hasattr(data, '_filename'):
            # Handle to linux case
            filename: Optional[str] = getattr(data, '_filename')
            if filename is None:
                return text
            # Linux returns '/etc/localtime'
            if Path(filename).is_symlink():
                # we need to resolve the symbolic link
                filename = os.path.realpath(filename)

            # The complete path will have this format /usr/share/zoneinfo/America/Chicago
            # We only want the last two: America/Chicago
            text = "/".join(filename.split('/')[-2:])
        elif hasattr(data, '_tznames'):
            # Handle the Windows case
            names: tuple[str] = getattr(data, '_tznames')
            if len(names) > 0:  # pylint: disable=W0212; protected-access
                text = convert_windows_tz_name_to_iani_name(names[0])  # pylint: disable=W0212; protected-access

        return text


class DataProcessor_zoneinfo(DataProcessorAbstractBaseClass):
    """
    Encode a zoneinfo value.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'zoneinfo'

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_zoneinfo_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return self._classifier.is_zoneinfo(data)

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return str(data.key)


class DataProcessor_post_processor_for_classes(DataProcessorAbstractBaseClass):
    """
    Encode an object.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return data.__class__.__name__

    @override
    def _get_element_name_from_config(self) -> Optional[str]:
        return self.config.override_class_label

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        # can we iterate over its values?
        # Does it have a __dict__ we iterate over?
        return hasattr(data, '__dict__') and \
            not inspect.isfunction(data) and \
            not inspect.ismethod(data)

    @override
    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        for attr in dir(data):
            if attr.startswith("__") and attr.endswith("__"):  # skip the 'magic' objects
                continue
            attr_name = attr
            val = getattr(data, attr)
            if callable(val):  # skip methods
                continue
            self._process(
                config=self.config,
                parent=current,
                data=val,
                child_name=attr_name
            )


class DataProcessor_used_for_testing(DataProcessorAbstractBaseClass):
    """
    Used for testing.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'DataProcessor_used_for_testing'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return True

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return None

    @override
    def _try_converting(
        self,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        return None  # pragma: no coverage


class DataProcessor_used_for_testing_use_hints(DataProcessorAbstractBaseClass):
    """
    Used for testing.
    """

    @override
    def _get_default_element_name(self, data: Any) -> str:
        return 'DataProcessor_used_for_testing_use_hints'

    @override
    def _is_expected_data_type(self, data: Any) -> bool:
        return True

    @override
    def _get_textual_representation_of_data(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        return None

    @override
    def _get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'test- get_field_type_hint'

    @override
    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return 'test- get_format_string_hint'

    @override
    def _try_converting(
        self,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        return None  # pragma: no coverage
