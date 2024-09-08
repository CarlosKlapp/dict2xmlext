"""
Base class for configuration.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple, TypeAlias
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import re
from libs.codec_wrapper import CodecWrapper
from libs.attributes import AttributeFlags, AttributeFlagsNames

DATA_PROCESSOR_RETURN_TYPE: TypeAlias = ET.Element | None


@dataclass
class BuilderConfig_BaseClass(ABC):
    root_label: str = 'root'

    override_binary_label: Optional[str] = None
    override_bool_label: Optional[str] = None
    override_calendar_label: Optional[str] = None
    override_chainmap_label: Optional[str] = None
    override_child_item_label: Optional[str] = None
    override_class_label: Optional[str] = None
    override_date_label: Optional[str] = None
    override_datetime_label: Optional[str] = None
    override_dict_label: Optional[str] = None
    override_enum_label: Optional[str] = None
    override_namedtuple_label: Optional[str] = None
    override_none_label: Optional[str] = None
    override_numeric_label: Optional[str] = None
    override_sequence_label: Optional[str] = None
    override_str_label: Optional[str] = None
    override_time_label: Optional[str] = None
    override_timedelta_label: Optional[str] = None
    override_tzinfo_label: Optional[str] = None
    override_unknown_object_label: Optional[str] = None
    override_zoneinfo_label: Optional[str] = None

    label_invalid_xml_element_name: str = 'inv_tag_placeholder'
    label_invalid_xml_element_name_attribute: str = 'original_element_name'

    _codec_binary: CodecWrapper = CodecWrapper()
    _codec_text: CodecWrapper = CodecWrapper()

    _regex_pattern_is_valid_element_name = re.compile(r'[_a-zA-Z]\w*')

    def is_valid_xml_element_name(self, tag: str) -> bool:
        return self._regex_pattern_is_valid_element_name.fullmatch(tag) is not None

    def fix_invalid_xml_element_name(self, tag: str) -> Tuple[str, Dict[str, str]]:
        if self.is_valid_xml_element_name(tag):
            return (tag, {})
        else:
            return (self.label_invalid_xml_element_name, {self.label_invalid_xml_element_name_attribute: tag})

    def get_codec_binary(self) -> CodecWrapper:
        return self._codec_binary

    def set_codec_binary(self, codec: CodecWrapper) -> None:
        self._codec_binary = codec

    codec_binary = property(get_codec_binary, set_codec_binary)

    def get_codec_text(self) -> CodecWrapper:
        return self._codec_text

    def set_codec_text(self, codec: CodecWrapper) -> None:
        self._codec_text = codec

    codec_text = property(get_codec_text, set_codec_text)

    attr_flags: AttributeFlags = AttributeFlags.NONE
    attr_flag_names: Dict[AttributeFlags, str] = field(default_factory=lambda: AttributeFlagsNames)

    def __post_init__(self) -> None:
        self.codec_binary.codec_name = 'base64'

    @abstractmethod
    def _process_helper(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs: object) -> DATA_PROCESSOR_RETURN_TYPE:
        pass  # pragma: no cover

    @abstractmethod
    def process(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs: object) -> DATA_PROCESSOR_RETURN_TYPE:
        pass  # pragma: no cover

    @abstractmethod
    def include_seq_id_as_attribute(self) -> Dict[str, str]:
        pass  # pragma: no cover

    @abstractmethod
    def Element(self, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs: object) -> ET.Element:
        pass  # pragma: no cover

    @abstractmethod
    def SubElement(self, parent: ET.Element, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs: object) -> ET.Element:
        pass  # pragma: no cover


CLASS_BUILDER_CONFIG: TypeAlias = "BuilderConfig_BaseClass"
DATA_PROCESSOR_FUNC_TYPE: TypeAlias = Callable[[CLASS_BUILDER_CONFIG, ET.Element, Any], DATA_PROCESSOR_RETURN_TYPE]
