# pylint: disable=C0302; too-many-lines
"""
Base class for configuration and formatting data.
"""

from abc import ABC, abstractmethod
from collections import abc
import re
from typing import Any, Callable, Dict, Final, List, Optional, Tuple, TypeAlias
import uuid
from libs.attributes import ATTRIBUTE_FLAGS_NAMES, AttributeFlags
from libs.codec_wrapper import CodecWrapper
from libs.data_type_identification import DataTypeIdentification


XmlAttributesTypeAlias: TypeAlias = Dict[str, str]
OptionalXmlAttributesTypeAlias: TypeAlias = Optional[XmlAttributesTypeAlias]


ConfigTypeAlias: TypeAlias = "ConfigBaseClass"
"""
Type alias for the config base class.
"""


XmlElementTypeAlias: TypeAlias = "XmlElementNameBaseClass"
"""
Type alias for `XmlElementTypeAlias`. This is an argument type
of most methods in this library.
"""

OptionalXmlElementTypeAlias: TypeAlias = Optional[XmlElementTypeAlias]
"""
Type alias for `XmlElementTypeAlias`. This is an argument type
of most methods in this library.
"""

DataProcessorReturnTypeAlias: TypeAlias = OptionalXmlElementTypeAlias
"""
Type alias for `OptionalXmlElementTypeAlias`. This is the return type
of most methods in this library.
"""

DataProcessorFuncTypeAlias: TypeAlias = Callable[
    [ConfigTypeAlias, XmlElementTypeAlias, Any],
    DataProcessorReturnTypeAlias
]
"""
Type alias for the return type of most methods.
"""


class ConfigBaseClass(ABC):
    """
    Abstract base class for holding configuration and formatting data.
    """

    def __init__(self):
        self.root_label: str = 'root'

        self.override_binary_label: Optional[str] = None
        self.override_bool_label: Optional[str] = None
        self.override_calendar_label: Optional[str] = None
        self.override_chainmap_label: Optional[str] = None
        self.override_child_item_label: Optional[str] = None
        self.override_class_label: Optional[str] = None
        self.override_date_label: Optional[str] = None
        self.override_datetime_label: Optional[str] = None
        self.override_dict_label: Optional[str] = None
        self.override_enum_label: Optional[str] = None
        self.override_namedtuple_label: Optional[str] = None
        self.override_none_label: Optional[str] = None
        self.override_numeric_label: Optional[str] = None
        self.override_sequence_label: Optional[str] = None
        self.override_str_label: Optional[str] = None
        self.override_time_label: Optional[str] = None
        self.override_timedelta_label: Optional[str] = None
        self.override_tzinfo_label: Optional[str] = None
        self.override_unknown_object_label: Optional[str] = None
        self.override_zoneinfo_label: Optional[str] = None

        self.label_invalid_xml_element_name: str = 'inv_tag_placeholder'
        self.label_invalid_xml_element_name_attribute: str = 'original_element_name'

        self._codec_binary: CodecWrapper = CodecWrapper()
        """
        Encoder for binary to text.
        """

        self._codec_text: CodecWrapper = CodecWrapper()
        """
        Encoder for text data.
        """

        self.attr_flags: AttributeFlags = AttributeFlags.NONE
        """
        List of desired attributes to be including in the JSOn to XML encoding.
        """
        # Make a copy of the ATTRIBUTE_FLAGS_NAMES in case the derived calss wishes
        # to make changes.
        self.attr_flag_names: Dict[AttributeFlags, str] = ATTRIBUTE_FLAGS_NAMES.copy()
        """
        Names of the attributes. You can safely modify this dictionary for customization.
        """

        self._elements_sequential_counter: int = 0
        """
        Variable for the sequential element counter.

        Reset this to zero before you begin transform JSON to XML.
        """

        # These variables need to populated by child classes.
        self.custom_pre_processors: List[DataProcessorAbstractBaseClass] = []
        self.default_processors: List[DataProcessorAbstractBaseClass] = []
        self.custom_post_processors: List[DataProcessorAbstractBaseClass] = []
        self.last_chance_processor: DataProcessorAbstractBaseClass

        self.data_type_identifier: DataTypeIdentification
        """
        Used to identify the type of data so the appropriate encoder can be called.

        Holds a reference to DataTypeIdentification.
        """

        self.xml_element_name_fixer: XmlElementNameBaseClass
        """
        Used to fix the name of an XML element name.

        Holds a reference to XmlElementNameBaseClass
        """

    @property
    def elements_sequential_counter(self) -> int:
        """
        Get the current value of the counter.
        """
        return self._elements_sequential_counter

    @elements_sequential_counter.setter
    def elements_sequential_counter(self, value: int):
        self._elements_sequential_counter = value

    def increment_elements_sequential_counter(self) -> int:
        """
        Increment the counter and return the newly incremented value.

        Returns:
            int: Newly incremented value.
        """
        self._elements_sequential_counter += 1
        return self._elements_sequential_counter

    def get_codec_binary(self) -> CodecWrapper:
        """
        Getter for the binary codec.

        Returns:
            CodecWrapper: Class encapsulating a binary codec.
        """
        return self._codec_binary

    def set_codec_binary(self, codec: CodecWrapper) -> None:
        """
        Setter for the binary codec.

        Args:
            codec (CodecWrapper): Class encapsulating a binary codec.
        """
        self._codec_binary = codec

    codec_binary = property(get_codec_binary, set_codec_binary)
    """
    Getter / Setter for the binary codec
    """

    def get_codec_text(self) -> CodecWrapper:
        """
        Getter for the text codec.

        Returns:
            CodecWrapper: Class encapsulating a binary codec.
        """
        return self._codec_text

    def set_codec_text(self, codec: CodecWrapper) -> None:
        """
        Setter for the text codec.

        Args:
            codec (CodecWrapper): Class encapsulating a binary codec.
        """
        self._codec_text = codec

    codec_text = property(get_codec_text, set_codec_text)
    """
    Getter / Setter for the text codec
    """

    def __post_init__(self) -> None:
        self.codec_binary.codec_name = 'base64'

    def make_attribute(
        self,
        attr_flag: AttributeFlags,
        value: str
    ) -> XmlAttributesTypeAlias:
        """
        Given an integer and str, create a dictionary that will
        be used for attributes.

        Args:
            attr_flag (AttributeFlags): _description_
            value (str): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        return {self.attr_flag_names[attr_flag]: value}


class DataProcessorAbstractBaseClass(ABC):
    """
    Abstract base class for data processors. Child classes are responsible for encoding
    a single data type to a textual representation.

    This abstract class implements many of the methods. Child
    classes need to override the following methods to encode the data:\n
        get_default_element_name
        get_element_name_from_config
        is_expected_data_type
        get_textual_representation_of_data
    If the data has nested data like a dictionary or list, the
    child class should also override:\n
        _recursively_process_any_nested_objects
    """

    def __init__(self, config: ConfigTypeAlias):
        self._classifier: DataTypeIdentification = DataTypeIdentification()
        self.config = config

    @property
    def classifier(self) -> DataTypeIdentification:
        """
        Getter Setter the current ObjectClassifier.

        Returns:
            ObjectClassifier: current ObjectClassifier
        """
        return self._classifier

    @classifier.setter
    def classifier(self, value: DataTypeIdentification):
        self._classifier = value

    @abstractmethod
    def get_default_element_name(self, data: Any) -> str:
        """
        Return the default element name of the XML -> `<element_name>...</element_name>`.

        Args:
            data (Any): data to be encoded as XML

        Returns:
            str: element name
        """

    @abstractmethod
    def is_expected_data_type(self, data: Any) -> bool:
        """
        Indicates whether this class can endode this data type.

        Args:
            data (Any): _description_

        Returns:
            bool: True if the class can encode this data type, False otherwise.
        """

    def _recursively_process_any_nested_objects(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> None:
        """
        If the arg `data` contains any nested objects, this method will
        recursively encode the nested objects.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            _type_: _description_
        """

    def _get_textual_representation_of_data(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> Optional[str]:
        """
        Converts the data into text for placement inside the XML
        element -> `<element_name>text</element_name>`.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            Optional[str]: Data converted to a textual representation or None.
        """
        return None

    def _get_element_name_from_config(self) -> Optional[str]:
        """
        Retrieve the overridden XML element name from the configuration class.
        Element name -> `<element_name>...</element_name>`

        Returns:
            Optional[str]: Return the overriden name or None.
        """
        return None

    def _get_element_name(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
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
            parent (XmlElementTypeAlias): _description_
            data (Any): _description_
            child_name (Optional[str], optional): XML element name. Defaults to None.

        Returns:
            str: XML element name.
        """
        return child_name \
            or self._get_element_name_from_config() \
            or self.get_default_element_name(data)

    def _get_field_type_hint(self, data: Any, **kwargs: object) -> Optional[str]:  # pylint: disable=W0613;unused-argument
        """
        Adds a hint in the XML attributes as to the type of data that was encoded
        to text.

        For example, `<element_name type_hint="namedtuple">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Data type hint or None.
        """
        return None

    def _get_field_comment(self, data: Any, **kwargs: object) -> Optional[str]:  # pylint: disable=W0613;unused-argument
        """
        Return a comment to be added in the XML element as an attribute.

        For example, `<element_name comment="IANA time zone database key
        (e.g. America/New_York, Europe/Paris or Asia/Tokyo)">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Comment to add as an attribute or None.
        """
        return None

    def _get_format_string_hint(self, data: Any, **kwargs: object) -> Optional[str]:  # pylint: disable=W0613;unused-argument
        """
        Return a hint about the data format in the XML element.

        For example, `<element_name format_string_hint="YYYYMMDD">...</element_name>`

        Args:
            data (Any): _description_

        Returns:
            Optional[str]: Format of the data or None.
        """
        return None

    def _try_converting(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        """
        _summary_

        Args:
            parent (XmlElementTypeAlias): _description_
            data (Any): _description_
            child_name (Optional[str], optional): _description_. Defaults to None.

        Returns:
            DATA_PROCESSOR_RETURN_TYPE: _description_
        """
        if not self.is_expected_data_type(data):
            return None

        new_tag: str = self._get_element_name(
            parent=parent,
            data=data,
            child_name=child_name
        )
        current = parent.create_child_element(self.config, new_tag)
        text = self._get_textual_representation_of_data(  # pylint: disable=E1128; assignment-from-none
            parent=parent,
            current=current,
            data=data
        )
        if text is not None:
            current.text = text
        self._recursively_process_any_nested_objects(
            parent=parent,
            current=current,
            data=data
        )
        return current

    def try_converting_add_attributes(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        """
        _summary_

        Args:
            parent (XmlElementTypeAlias): _description_
            data (Any): _description_
            child_name (Optional[str], optional): _description_. Defaults to None.

        Returns:
            DATA_PROCESSOR_RETURN_TYPE: _description_
        """
        e = self._try_converting(
            config=self.config,
            parent=parent,
            data=data,
            child_name=child_name
        )
        if e is None:
            return None
        self._add_attributes(config=self.config, parent=parent, current=e, data=data)
        return e

    @classmethod
    def convert_to_xml(
        cls,
        config: ConfigTypeAlias,
        data: Any,
        attrib: OptionalXmlAttributesTypeAlias = None,
        **kwargs: object
    ) -> XmlElementTypeAlias:
        """
        Main method for converting an object to XML.

        Args:
            config (ConfigTypeAlias): _description_
            data (Any): _description_
            attrib (OptionalXmlAttributesTypeAlias, optional): _description_. Defaults to None.

        Returns:
            XmlElementTypeAlias: _description_
        """
        config.elements_sequential_counter = 0
        root: XmlElementTypeAlias = XmlElementNameBaseClass.create_root_element(
            config=config,
            tag=None,
            attrib=attrib,
            kwargs=kwargs
        )

        cls._process(config=config, parent=root, data=data, child_name=None, **kwargs)
        return root

    @classmethod
    def _locate_appropriate_data_processor(
        cls,
        config: ConfigTypeAlias,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        e: DataProcessorReturnTypeAlias = None

        for processor in config.custom_pre_processors:
            e = processor.try_converting_add_attributes(
                config=config,
                parent=parent,
                data=data,
                child_name=child_name,
                **kwargs
            )
            if e is not None:
                return e

        for processor in config.default_processors:
            e = processor.try_converting_add_attributes(
                config=config,
                parent=parent,
                data=data,
                child_name=child_name,
                **kwargs
            )
            if e is not None:
                return e

        for processor in config.custom_post_processors:
            e = processor.try_converting_add_attributes(
                config=config,
                parent=parent,
                data=data,
                child_name=child_name,
                **kwargs
            )
            if e is not None:
                return e

        e = config.last_chance_processor.try_converting_add_attributes(
            config=config,
            parent=parent,
            data=data,
            child_name=child_name,
            **kwargs
        )
        return e

    @classmethod
    def _process(
        cls,  # pylint: disable=W0613; unused-arguments -> kwargs
        config: ConfigTypeAlias,
        parent: XmlElementTypeAlias,
        data: Any,
        child_name: Optional[str] = None,
        **kwargs: object
    ) -> DataProcessorReturnTypeAlias:
        e = cls._locate_appropriate_data_processor(
            config=config,
            parent=parent,
            data=data,
            child_name=child_name
        )
        assert e is not None
        return e

    def _attr_alt_id(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_ALT_ID attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_ALT_ID
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        return {key: str(uuid.uuid4())}

    def _attr_binary_encoding(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_BINARY_ENCODING attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_BINARY_ENCODING
        return {ATTRIBUTE_FLAGS_NAMES[attrflag]: self.config.codec_binary.codec.name}

    def _attr_debug_info(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_DEBUG_INFO attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_DEBUG_INFO
        return {ATTRIBUTE_FLAGS_NAMES[attrflag]: f'processed_by:{self.__class__.__name__}'}

    def _attr_field_comment(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_FIELD_COMMENT attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_COMMENT
        attr: XmlAttributesTypeAlias = {}
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        hint = self._get_field_comment(data, **kwargs)  # pylint: disable=E1128; assignment-from-none
        if hint is not None:
            attr[key] = hint
        return attr

    def _attr_field_type_hint(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_FIELD_TYPE_HINT attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FIELD_TYPE_HINT
        attr: XmlAttributesTypeAlias = {}
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        hint = self._get_field_type_hint(data, **kwargs)  # pylint: disable=E1128; assignment-from-none
        if hint is not None:
            attr[key] = hint
        return attr

    def _attr_format_string_hint(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_FORMAT_STRING_HINT attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_FORMAT_STRING_HINT
        attr: XmlAttributesTypeAlias = {}
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        hint = self._get_format_string_hint(data, **kwargs)  # pylint: disable=E1128; assignment-from-none
        if hint is not None:
            attr[key] = hint
        return attr

    def _attr_len(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_LEN attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_LEN
        attr: XmlAttributesTypeAlias = {}
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        assert isinstance(data, abc.Sized)
        assert hasattr(data, '__len__')
        size: int
        try:
            size = len(data)
        except Exception:  # pylint: disable=W0718
            # W0718 - Catching too general exception
            size = 0 if current.text is None else len(current.text)
        attr[key] = str(size)
        return attr

    def _attr_python_data_type(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_PYTHON_DATA_TYPE attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_PYTHON_DATA_TYPE
        # type has the form "<class 'int'>". Use [1:-1] to convert it to "class 'int'"
        return {ATTRIBUTE_FLAGS_NAMES[attrflag]: str(type(data))[1:-1]}  # type: ignore

    def _attr_length_element_text(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_LENGTH_ELEMENT_TEXT attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_LENGTH_ELEMENT_TEXT
        attr: XmlAttributesTypeAlias = {}
        key: Final[str] = ATTRIBUTE_FLAGS_NAMES[attrflag]
        size = size = 0 if current.text is None else len(current.text)
        attr[key] = str(size)
        return attr

    def _attr_xsd_data_type(  # pylint: disable=W0613;unused-argument
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> XmlAttributesTypeAlias:
        """
        Returns a dictionary with the INC_XSD_DATA_TYPE attribute.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_

        Returns:
            XmlAttributesTypeAlias: _description_
        """
        attrflag: Final[AttributeFlags] = AttributeFlags.INC_XSD_DATA_TYPE
        return {ATTRIBUTE_FLAGS_NAMES[attrflag]: 'anyType'}

    def _add_attributes(
        self,
        parent: XmlElementTypeAlias,
        current: XmlElementTypeAlias,
        data: Any,
        **kwargs: object
    ) -> None:
        """
        Based on which attrbiute flags have been set in the configuration,
        and this method will call the appropriate attribute methods and attach
        the results to the XML element.

        Args:
            parent (XmlElementTypeAlias): _description_
            current (XmlElementTypeAlias): _description_
            data (Any): _description_
        """
        attr: XmlAttributesTypeAlias = {}

        if (
            (AttributeFlags.INC_BINARY_ENCODING & self.config.attr_flags) and
            self._classifier.is_binary(data)
        ):
            a = self._attr_binary_encoding(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_DEBUG_INFO & self.config.attr_flags:
            a = self._attr_debug_info(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_FIELD_COMMENT & self.config.attr_flags) \
                and self._get_field_comment(data, **kwargs) is not None:
            a = self._attr_field_comment(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (
            (AttributeFlags.INC_FIELD_TYPE_HINT & self.config.attr_flags)
            and self._get_field_type_hint(data, **kwargs) is not None
        ):
            a = self._attr_field_type_hint(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_FORMAT_STRING_HINT & self.config.attr_flags) \
                and self._get_format_string_hint(data, **kwargs) is not None:
            a = self._attr_format_string_hint(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if (AttributeFlags.INC_LEN & self.config.attr_flags) and isinstance(data, abc.Sized):
            a = self._attr_len(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_PYTHON_DATA_TYPE & self.config.attr_flags:
            a = self._attr_python_data_type(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        # Don't process AttributeFlags.INC_SEQ_ID here.
        # It is processed and added when the Element is created.

        if AttributeFlags.INC_LENGTH_ELEMENT_TEXT & self.config.attr_flags:
            a = self._attr_length_element_text(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        if AttributeFlags.INC_XSD_DATA_TYPE & self.config.attr_flags:
            a = self._attr_xsd_data_type(
                parent=parent,
                current=current,
                data=data,
                **kwargs
            )
            attr |= a

        current.attributes |= attr


class XmlElementNameBaseClass:
    """
    Abstract base class responsible for creating XML elements and
    determining the validity of an XML element name
    and fixing the name so it conforms the XML standard.
    """

    _DEFAULT_REGEX_PATTERN_IS_VALID_ELEMENT_NAME: Final[re.Pattern[str]] = \
        re.compile(r'[_a-zA-Z]\w*')
    """
    Class variable.
    The default regular expression pattern used to determine if an XML
    element name is valid. Do not modify. Instead override the
    instance variable `regex_pattern_is_valid_element_name`.
    """

    def __init__(
        self,
        config: ConfigTypeAlias,
        tag: str,
        attrib: OptionalXmlAttributesTypeAlias,
        parent: OptionalXmlElementTypeAlias
    ) -> None:
        self.config = config
        """
        Reference to the config information.
        """

        self.regex_pattern_is_valid_element_name: re.Pattern[str] = \
            self._DEFAULT_REGEX_PATTERN_IS_VALID_ELEMENT_NAME
        """
        The regular expression pattern that will be used by this instance.
        Override this variable to change the instance behavior.
        """

        # set the parent of this class
        self.parent: OptionalXmlElementTypeAlias = parent
        """
        Reference to the parent of this node. If this is a root
        element, the parent is None.
        """
        # If we have a parent, append self to their list of children.
        if parent is not None:
            parent.children.append(self)

        self.children: List[XmlElementTypeAlias] = []
        """
        List of child elements.
        """

        self.text: Optional[str] = None
        """
        Text within the element. `<tag>text</tag>`
        """

        self.attributes: XmlAttributesTypeAlias = {}
        """
        Attributes to be added to the XML element.
        """
        if attrib is not None:
            self.attributes |= attrib

        new_tag, old_tag = self.fix_invalid_xml_element_name(tag)
        self.attributes |= old_tag
        self.tag: str = new_tag
        """
        Name of the element. `<tag>text</tag>`
        """

    def is_valid_xml_element_name(
        self,
        tag: str
    ) -> bool:
        """
        Determines if the tag is a proper name for an XML element.
        `<element_name> ... </element_name>`
        Override this method to change how an invlid XML element
        name is determined.

        Args:
            config (ConfigTypeAlias): _description_
            tag(str): Element name.

        Returns:
            bool: True if valid, otherwise False.
        """
        return self.regex_pattern_is_valid_element_name.fullmatch(tag) is not None

    def fix_invalid_xml_element_name(
        self,
        tag: str
    ) -> Tuple[str, XmlAttributesTypeAlias]:
        """
        Create a valid XML element name.
        `<element_name>...</element_name>`
        Override this method to change how the invalid element
        name will be corrected.

        Args:
            config (ConfigTypeAlias): _description_
            tag (str): Element name.

        Returns:
            Tuple[str, XmlAttributesTypeAlias]:
            Returns a tuple with the following information:
            Tuple('valid_element_name', {"attribute_name": "attribute_value"})
        """
        if self.is_valid_xml_element_name(tag):
            return (tag, {})
        else:
            return (
                self.config.label_invalid_xml_element_name,
                {self.config.label_invalid_xml_element_name_attribute: tag}
            )

    @classmethod
    def create_root_element(
        cls,
        config: ConfigTypeAlias,
        tag: Optional[str],
        attrib: OptionalXmlAttributesTypeAlias = None,
        **kwargs: object
    ) -> XmlElementTypeAlias:
        """
        Add a root XML element.

        Args:
            config (ConfigTypeAlias): _description_
            tag (Optional[str]): The name of the element `<tag>...</tag>`. If None, then the
                `config.root_label` is used.
            attrib (OptionalXmlAttributesTypeAlias, optional): _description_. Defaults to None.

        Returns:
            XmlElementTypeAlias: _description_
        """
        return cls._factory_create_child_element(
            config=config,
            parent=None,
            tag=config.root_label if tag is None else tag,
            attrib=attrib,
            kwargs=kwargs
        )

    @abstractmethod
    def create_child_element(
        self,
        config: ConfigTypeAlias,
        tag: str,
        attrib: OptionalXmlAttributesTypeAlias = None,
        **kwargs: object
    ) -> XmlElementTypeAlias:
        """
        Add a child XML element.

        Args:
            config (ConfigTypeAlias): _description_
            parent (XmlElementTypeAlias): _description_
            tag (str): The name of the element `<tag>...</tag>`.
            attrib (OptionalXmlAttributesTypeAlias, optional): _description_. Defaults to None.

        Returns:
            XmlElementTypeAlias: _description_
        """
        return self._factory_create_child_element(
            config=config,
            parent=self,
            tag=tag,
            attrib=attrib,
            kwargs=kwargs
        )

    @classmethod
    def _factory_create_child_element(
        cls,  # pylint: disable=W0613; unused-arguments -> kwargs
        config: ConfigTypeAlias,
        parent: OptionalXmlElementTypeAlias,
        tag: str,
        attrib: OptionalXmlAttributesTypeAlias = None,
        **kwargs: object
    ) -> XmlElementTypeAlias:
        """
        Internal helper to actually create the XML element.

        Args:
            config (ConfigTypeAlias): _description_
            parent (XmlElementTypeAlias): _description_
            tag (str): _description_
            attrib (Optional[Dict[int, str]], optional): _description_. Defaults to None.

        Returns:
            XmlElementTypeAlias: _description_
        """
        element: XmlElementNameBaseClass = XmlElementNameBaseClass(config, tag, attrib, parent)
        counter: int = config.increment_elements_sequential_counter()  # always increment

        if AttributeFlags.INC_SEQ_ID & config.attr_flags:
            element.attributes |= config.make_attribute(AttributeFlags.INC_SEQ_ID, str(counter))

        return element
