from abc import ABC
from abc import abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple, TypeAlias
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import re
from libs.codec_wrapper import CodecWrapper
from libs.attributes import AttributeFlags, AttributeFlagsNames

DATA_PROCESSOR_RETURN_TYPE: TypeAlias = Optional[ET.Element]


@ dataclass
class BuilderConfig_BaseClass(ABC):
    root_label: str = 'root'
    default_ChainMap_label: str = 'ChainMap'
    default_dict_label: str = 'dict'
    default_sequence_label: str = 'sequence'
    default_namedtuple_label: str = 'namedtuple'
    default_item_label: str = 'item'
    default_label: str = 'unknown_object'
    default_label_invalid_xml_element_name: str = 'inv_tag_placeholder'
    default_label_invalid_xml_element_name_attribute: str = 'original_element_name'

    _codec_binary: CodecWrapper = CodecWrapper()
    _codec_text: CodecWrapper = CodecWrapper()

    _regex_pattern_is_valid_element_name = re.compile(r'[_a-zA-Z]\w*')

    def is_valid_xml_element_name(self, tag: str) -> bool:
        return self._regex_pattern_is_valid_element_name.fullmatch(tag) is not None

    def fix_invalid_xml_element_name(self, tag: str) -> Tuple[str, Dict[str, str]]:
        if self.is_valid_xml_element_name(tag):
            return (tag, {})
        else:
            return (self.default_label_invalid_xml_element_name, {self.default_label_invalid_xml_element_name_attribute: tag})

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
    def _process_helper(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        pass  # pragma: no cover

    @abstractmethod
    def process(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> DATA_PROCESSOR_RETURN_TYPE:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_dict_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_ChainMap_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_sequence_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_namedtuple_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_item_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_default_name(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def include_seq_id_as_attribute(self) -> Dict[str, str]:
        pass  # pragma: no cover

    @abstractmethod
    def Element(self, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs) -> ET.Element:
        pass  # pragma: no cover

    @abstractmethod
    def SubElement(self, parent: ET.Element, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs) -> ET.Element:
        pass  # pragma: no cover


CLASS_BUILDER_CONFIG: TypeAlias = "BuilderConfig_BaseClass"
DATA_PROCESSOR_FUNC_TYPE: TypeAlias = Callable[[CLASS_BUILDER_CONFIG, ET.Element, Any], DATA_PROCESSOR_RETURN_TYPE]
