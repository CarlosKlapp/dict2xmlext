"""
Definicion of the abstract base class. Prevents linters from complaining.
"""
from abc import abstractmethod
import array
import enum
from typing import Any, Dict, Optional, final
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from collections import abc, ChainMap, deque
# from dataclasses import dataclass, field
import datetime as dt
import numbers
# import time
import calendar
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE


class DataProcessorAbstractBaseClass:
    """
    Without this base class the linter complains about the methods returning None.
    Use this unnecessary abstract class to keep the linter from complaining.
    """

    @abstractmethod
    def get_default_element_name(self, config: CLASS_BUILDER_CONFIG, data: Any) -> str:
        """
        Return the default element name of the XML -> `<element_name>...</element_name>`.

        Args:
            config (CLASS_BUILDER_CONFIG): Configuration and formatting data.
            data (Any): data to be encoded as XML

        Returns:
            str: element name
        """

    @abstractmethod
    def is_expected_data_type(self, data: Any) -> bool:
        """
        Can this class can endode this data type.

        Args:
            data (Any): _description_

        Returns:
            bool: True if the class can encode this data type, False otherwise.
        """

    @abstractmethod
    def recursively_process_any_nested_objects(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> None:
        """
        _summary_

        Args:
            config (CLASS_BUILDER_CONFIG): _description_
            parent (ET.Element): _description_
            current (ET.Element): _description_
            data (Any): _description_

        Returns:
            _type_: _description_
        """

    @abstractmethod
    def get_textual_representation_of_data(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        """
        Converts the data into text for placement inside the XML
        element -> `<element_name>text</element_name>`.

        Args:
            config (CLASS_BUILDER_CONFIG): _description_
            parent (ET.Element): _description_
            current (ET.Element): _description_
            data (Any): _description_

        Returns:
            Optional[str]: Data converted to a textual representation or None.
        """

    @abstractmethod
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        """
        Retrieve the overridden XML element name from the configuration class.
        Element name -> `<element_name>...</element_name>`

        Args:
            config (CLASS_BUILDER_CONFIG): _description_

        Returns:
            Optional[str]: Return the overriden name or None.
        """

    @abstractmethod
    def get_element_name(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> str:
        """
        Return the element name of the XML -> `<element_name>...</element_name>`.
        The default implementation will return the first non-None value.

        return child_name \
            or self.get_element_name_from_config(config) \
            or self.get_default_element_name(config, data)

        Args:
            config (CLASS_BUILDER_CONFIG): _description_
            parent (ET.Element): _description_
            data (Any): _description_
            child_name (Optional[str], optional): XML element name. Defaults to None.

        Returns:
            str: XML element name.
        """

    @abstractmethod
    def get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        """
        Adds a hint in the XML attributes as to the type of data that was encoded
        to text.

        For example, `<element_name type_hint="namedtuple">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Data type hint or None.
        """

    @abstractmethod
    def get_field_comment(self, data: Any, **kwargs: object) -> Optional[str]:
        """
        Return a comment to be added in the XML element as an attribute.

        For example, `<element_name comment="IANA time zone database key (e.g. America/New_York, Europe/Paris or Asia/Tokyo)">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Comment to add as an attribute or None.
        """

    @abstractmethod
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        """
        Return a hint about the data format in the XML element.

        For example, `<element_name format_string_hint="YYYYMMDD">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Format of the data or None.
        """

    @abstractmethod
    def create_tree(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        pass

    @abstractmethod
    def process(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element, data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        pass

    @abstractmethod
    def attr_alt_id(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_binary_encoding(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_debug_info(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_field_comment(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_field_type_hint(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_format_string_hint(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_len(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_python_data_type(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_size_bytes(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def attr_xsd_data_type(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def add_attributes(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> None:
        pass

    @final
    @staticmethod
    def is_bytes(data: Any) -> bool:
        return isinstance(data, bytes)

    @final
    @staticmethod
    def is_bytearray(data: Any) -> bool:
        return isinstance(data, bytearray)

    @final
    @staticmethod
    def is_binary(data: Any) -> bool:
        return DataProcessorAbstractBaseClass.is_bytes(data) \
            or DataProcessorAbstractBaseClass.is_bytearray(data)

    @final
    @staticmethod
    def is_bool(data: Any) -> bool:
        return isinstance(data, bool) and str(type(data)) == "<class 'bool'>"

    @final
    @staticmethod
    def is_calendar(data: Any) -> bool:
        return isinstance(data, calendar.Calendar)

    @final
    @staticmethod
    def is_chainmap(data: Any) -> bool:
        return isinstance(data, ChainMap)

    @final
    @staticmethod
    def is_date(data: Any) -> bool:
        return isinstance(data, dt.date) and not isinstance(data, dt.datetime)

    @final
    @staticmethod
    def is_datetime(data: Any) -> bool:
        return isinstance(data, dt.datetime)

    @final
    @staticmethod
    def is_dict(data: Any) -> bool:
        return isinstance(data, dict) or isinstance(data, abc.Mapping)

    @final
    @staticmethod
    def is_enum(data: Any) -> bool:
        return isinstance(data, enum.Enum)

    @final
    @staticmethod
    def is_namedtuple(data: Any) -> bool:
        # type: ignore
        return (
            isinstance(data, tuple) and
            hasattr(data, '_asdict') and  # type: ignore
            hasattr(data, '_fields')  # type: ignore
        )

    @final
    @staticmethod
    def is_none(data: Any) -> bool:
        return data is None

    @final
    @staticmethod
    def is_numeric(data: Any) -> bool:
        return isinstance(data, numbers.Number) \
            and (not isinstance(data, enum.Enum)) \
            and str(type(data)) != "<class 'bool'>"

    @final
    @staticmethod
    def is_sequence(data: Any) -> bool:
        return isinstance(data, list | tuple | set | range | array.array | deque | abc.Iterator) \
            and not DataProcessorAbstractBaseClass.is_namedtuple(data) \
            and not DataProcessorAbstractBaseClass.is_dict(data)

    @final
    @staticmethod
    def is_str(data: Any) -> bool:
        return isinstance(data, str)

    @final
    @staticmethod
    def is_time(data: Any) -> bool:
        return isinstance(data, dt.time)

    @final
    @staticmethod
    def is_timedelta(data: Any) -> bool:
        return isinstance(data, dt.timedelta)

    @final
    @staticmethod
    def is_timezone(data: Any) -> bool:
        return isinstance(data, dt.timezone)

    @final
    @staticmethod
    def is_zoneinfo(data: Any) -> bool:
        return isinstance(data, ZoneInfo)

    @final
    @staticmethod
    def is_tzinfo(data: Any) -> bool:
        return isinstance(data, dt.tzinfo) \
            and not DataProcessorAbstractBaseClass.is_timezone(data) \
            and not DataProcessorAbstractBaseClass.is_zoneinfo(data)
