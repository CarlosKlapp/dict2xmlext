# import array
# from ctypes import Array
# import enum
# from tokenize import Number
from typing import Any, Dict, List, Optional, Final
# from typing import Any, Callable, Dict, List, Optional, TypeAlias, cast, Final, final
import xml.etree.ElementTree as ET
# from collections.abc import Sized
from dataclasses import dataclass, field
# import datetime as dt
# import numbers
# import time
# import calendar
# import uuid
# import sys
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import BuilderConfig_BaseClass, DATA_PROCESSOR_RETURN_TYPE
from libs.data_processor import (
    DataProcessorBaseClass,
    DataProcessor_binary,
    DataProcessor_bool,
    DataProcessor_calendar,
    DataProcessor_post_processor_for_classes,
    DataProcessor_date,
    DataProcessor_datetime,
    DataProcessor_dict,
    DataProcessor_enum,
    DataProcessor_namedtuple,
    DataProcessor_none,
    DataProcessor_numeric,
    DataProcessor_sequence,
    DataProcessor_str,
    DataProcessor_time,
    DataProcessor_timedelta,
    DataProcessor_timezone,
    DataProcessor_tzinfo,
    DataProcessor_zoneinfo,
    DataProcessor_last_chance,
    DataProcessor_ChainMap
)


@ dataclass
class BuilderConfig(BuilderConfig_BaseClass):
    default_processors: List[DataProcessorBaseClass] = field(default_factory=lambda: [
        DataProcessor_binary(),
        DataProcessor_bool(),
        DataProcessor_calendar(),
        DataProcessor_ChainMap(),
        DataProcessor_date(),
        DataProcessor_datetime(),
        DataProcessor_dict(),
        DataProcessor_enum(),
        DataProcessor_none(),
        DataProcessor_numeric(),
        DataProcessor_namedtuple(),
        DataProcessor_sequence(),
        DataProcessor_str(),
        DataProcessor_time(),
        DataProcessor_timedelta(),
        DataProcessor_timezone(),
        DataProcessor_tzinfo(),
        DataProcessor_zoneinfo(),
    ])
    custom_pre_processors: List[DataProcessorBaseClass] = field(default_factory=list)
    custom_post_processors: List[DataProcessorBaseClass] = field(default_factory=lambda: [
        DataProcessor_post_processor_for_classes()
    ])
    last_chance_processor: DataProcessor_last_chance = DataProcessor_last_chance()
    num_elements_counter: int = 0

    def _process_helper(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs: object) -> DATA_PROCESSOR_RETURN_TYPE:
        for processor in self.custom_pre_processors:
            e = processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
            if (e is not None):
                return e

        for processor in self.default_processors:
            e = processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
            if (e is not None):
                return e

        for processor in self.custom_post_processors:
            e = processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
            if (e is not None):
                return e

        e = self.last_chance_processor.process(config=self, parent=parent, data=data, child_name=child_name, **kwargs)
        return e

    def process(self, parent: ET.Element, data: Any, child_name: Optional[str] = None, **kwargs: object) -> DATA_PROCESSOR_RETURN_TYPE:
        e = self._process_helper(parent=parent, data=data, child_name=child_name)
        assert e is not None

    def include_seq_id_as_attribute(self) -> Dict[str, str]:
        attrib: Dict[str, str] = {}
        if (AttributeFlags.INC_SEQ_ID & self.attr_flags):
            attrflag: Final[AttributeFlags] = AttributeFlags.INC_SEQ_ID
            key: Final[str] = AttributeFlagsNames[attrflag]
            attrib[key] = str(self.num_elements_counter)
        return attrib

    def Element(self, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs: object) -> ET.Element:
        self.num_elements_counter += 1
        extra = self.include_seq_id_as_attribute()
        if attrib:
            extra |= attrib
        tag, old_tag = self.fix_invalid_xml_element_name(tag)
        extra |= old_tag
        # Don't pass kwargs to Element, they will just get added as attrbiutes
        return ET.Element(tag, attrib=extra)

    def SubElement(self, parent: ET.Element, tag: str, attrib: Optional[Dict[str, str]] = None, **kwargs: object) -> ET.Element:
        self.num_elements_counter += 1
        extra = self.include_seq_id_as_attribute()
        if attrib:
            extra |= attrib
        tag, old_tag = self.fix_invalid_xml_element_name(tag)
        extra |= old_tag
        return ET.SubElement(parent, tag, attrib=extra)


class Builder:
    config: BuilderConfig

    def __init__(self, config: Optional[BuilderConfig] = None) -> None:
        if config is None:
            config = BuilderConfig()
        self.config = config

    def build(self, data: Any, attrib: Optional[Dict[str, str]] = None, **kwargs: object) -> ET.Element:
        self.config.num_elements_counter = 0
        root: ET.Element = self.config.Element(tag=self.config.root_label, attrib=attrib, **kwargs)
        self.config.process(parent=root, data=data, child_name=None, **kwargs)
        return root
