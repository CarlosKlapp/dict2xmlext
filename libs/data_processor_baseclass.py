"""
This is the base class for processing data.
"""
from typing import Any, Dict, Optional, Final, override
import uuid
import xml.etree.ElementTree as ET
from collections import abc
# from dataclasses import dataclass, field
import sys
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.data_processor_abstract_baseclass import DataProcessorAbstractBaseClass


class DataProcessorBaseClass(DataProcessorAbstractBaseClass):
    """
    [<class 'datetime.timezone'>, <class 'datetime.tzinfo'>, <class 'object'>]
    [<class 'dateutil.tz.tz.tzfile'>, <class 'dateutil.tz._common._tzinfo'>,
    <class 'datetime.tzinfo'>, <class 'object'>]
    [<class 'zoneinfo.ZoneInfo'>, <class 'datetime.tzinfo'>, <class 'object'>]
    """

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
    def get_element_name_from_config(self, config: CLASS_BUILDER_CONFIG) -> Optional[str]:
        return None

    @override
    def get_element_name(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> str:
        return child_name \
            or self.get_element_name_from_config(config) \
            or self.get_default_element_name(config, data)

    @override
    def get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return None

    @override
    def get_field_comment(self, data: Any, **kwargs: object) -> Optional[str]:
        return None

    @override
    def get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:
        return None

    @override
    def create_tree(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        if not self.is_expected_data_type(data):
            return None

        new_tag: str = self.get_element_name(
            config=config,
            parent=parent,
            data=data,
            child_name=child_name
        )
        current = config.SubElement(parent, new_tag)
        text = self.get_textual_representation_of_data(
            config=config,
            parent=parent,
            current=current,
            data=data
        )
        if text is not None:
            current.text = text
        self.recursively_process_any_nested_objects(
            config=config,
            parent=parent,
            current=current,
            data=data
        )
        return current

    @override
    def process(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DATA_PROCESSOR_RETURN_TYPE:
        e = self.create_tree(config=config, parent=parent, data=data, child_name=child_name)
        if e is None:
            return None
        self.add_attributes(config=config, parent=parent, current=e, data=data)
        return e

    @override
    def attr_alt_id(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_ALT_ID
        key: Final[str] = AttributeFlagsNames[attrflag]
        return {key: str(uuid.uuid4())}

    @override
    def attr_binary_encoding(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_BINARY_ENCODING
        return {AttributeFlagsNames[attrflag]: config.codec_binary.codec.name}

    @override
    def attr_debug_info(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_DEBUG_INFO
        return {AttributeFlagsNames[attrflag]: f'processed_by:{self.__class__.__name__}'}

    @override
    def attr_field_comment(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_COMMENT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_field_comment(data, **kwargs)
        if hint is not None:
            attr[key] = hint
        return attr

    @override
    def attr_field_type_hint(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_TYPE_HINT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_field_type_hint(data, **kwargs)
        if hint is not None:
            attr[key] = hint
        return attr

    @override
    def attr_format_string_hint(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FORMAT_STRING_HINT
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        hint = self.get_format_string_hint(data, **kwargs)
        if hint is not None:
            attr[key] = hint
        return attr

    @override
    def attr_len(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_LEN
        return {AttributeFlagsNames[attrflag]: str(len(data))}

    @override
    def attr_python_data_type(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_PYTHON_DATA_TYPE
        # type has the form "<class 'int'>". Use [1:-1] to convert it to "class 'int'"
        return {AttributeFlagsNames[attrflag]: str(type(data))[1:-1]}  # type: ignore

    @override
    def attr_size_bytes(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_SIZE_BYTES
        attr: Dict[str, str] = {}
        key: Final[str] = AttributeFlagsNames[attrflag]
        size = sys.getsizeof(data, -1)
        if size > 0:
            attr[key] = str(size)
        return attr

    @override
    def attr_xsd_data_type(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> Dict[str, str]:
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_XSD_DATA_TYPE
        return {AttributeFlagsNames[attrflag]: 'anyType'}

    @override
    def add_attributes(
        self,
        config: CLASS_BUILDER_CONFIG,
        parent: ET.Element,
        current: ET.Element,
        data: Any,
        **kwargs: object
    ) -> None:
        attr: Dict[str, str] = {}

        if (AttributeFlags.INC_BINARY_ENCODING & config.attr_flags) and self.is_binary(data):
            a = self.attr_binary_encoding(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_DEBUG_INFO & config.attr_flags:
            a = self.attr_debug_info(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_FIELD_COMMENT & config.attr_flags) \
                and self.get_field_comment(data, **kwargs) is not None:
            a = self.attr_field_comment(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (
            (AttributeFlags.INC_FIELD_TYPE_HINT & config.attr_flags)
            and self.get_field_type_hint(data, **kwargs) is not None
        ):
            a = self.attr_field_type_hint(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_FORMAT_STRING_HINT & config.attr_flags) \
                and self.get_format_string_hint(data, **kwargs) is not None:
            a = self.attr_format_string_hint(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_LEN & config.attr_flags) and isinstance(data, abc.Sized):
            a = self.attr_len(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_PYTHON_DATA_TYPE & config.attr_flags:
            a = self.attr_python_data_type(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        # Don't process AttributeFlags.INC_SEQ_ID here.
        # It is processed and added when the Element is created.

        if AttributeFlags.INC_SIZE_BYTES & config.attr_flags:
            a = self.attr_size_bytes(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_XSD_DATA_TYPE & config.attr_flags:
            a = self.attr_xsd_data_type(
                config=config,
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        current.attrib.update(attr)
