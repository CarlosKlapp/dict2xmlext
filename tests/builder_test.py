# from zoneinfo import ZoneInfo
# import array
# import calendar
# from collections import namedtuple
# import enum
from typing import Any, Dict, Final, Optional
import unittest
import xml.etree.ElementTree as ET
# import datetime as dt
from libs.builder import Builder, BuilderConfig
from libs.attributes import AttributeFlags
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.codec_wrapper import CodecWrapper
from libs.data_processor import DataProcessorBaseClass
# from libs.misc import coalesce
# from dateutil import tz
from tests.predefined_test_cases import MyClass, MySubClass, MySubSubClass, test_case
from tests.config_test_cases import test_cases_config_rewrite_expected_output


class TestBuilder(unittest.TestCase):
    def test_builder(self):
        config = BuilderConfig()
        # config.attr_flags = AttributeFlags.NONE
        config.attr_flags = AttributeFlags.INC_ALL_DEBUG
        builder = Builder(config)

        e: ET.Element = builder.build(test_case)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if test_cases_config_rewrite_expected_output:
            with open(
                './tests/expected_test_builder.INC_ALL_DEBUG.xml',
                'w',
                encoding="utf-8"
            ) as f:
                f.write(result)

        with open('./tests/expected_test_builder.INC_ALL_DEBUG.xml', 'r', encoding="utf-8") as f:
            expected = f.read()

        self.assertEqual(result, expected)

    def test_custom_data_processors_using_inheritance(self):
        class DataProcessor_MyClass(DataProcessorBaseClass):
            # @final
            @staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MyClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MyClass.is_instance_or_derived(data):
                    return None
                new_tag: str = data.__class__.__name__
                current = config.SubElement(parent, new_tag)
                config.process(parent=current, data=data.name, child_name='name')
                return current

        class DataProcessor_MySubClass(DataProcessor_MyClass):
            # @ final
            @ staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MySubClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MySubClass.is_instance_or_derived(data):
                    return None
                current = super().create_tree(config, parent, data, child_name, **kwargs)
                # should never happen since we already verified we are a descendant
                assert current is not None
                config.process(parent=current, data=data.ip_addr, child_name='ip_addr')
                config.process(parent=current, data=data.port, child_name='port')
                config.process(parent=current, data=data._MySubClass__private_instance_var, child_name='__private_instance_var')
                return current

        class DataProcessor_MySubSubClass(DataProcessor_MySubClass):
            # @ final
            @ staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MySubSubClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MySubSubClass.is_instance_or_derived(data):
                    return None
                current = super().create_tree(config, parent, data, child_name, **kwargs)
                # should never happen since we already verified we are a descendant
                assert current is not None
                config.process(parent=current, data=data.geolocation, child_name='geolocation')
                config.process(parent=current, data=data.instance_var, child_name='instance_var')
                return current

        # Verify the "is_" functions are recognizing the hierarchy
        my_class = MyClass()
        my_sub_class = MySubClass()
        my_sub_sub_class = MySubSubClass()

        self.assertTrue(DataProcessor_MyClass.is_instance_or_derived(my_class))
        self.assertTrue(DataProcessor_MyClass.is_instance_or_derived(my_sub_class))
        self.assertTrue(DataProcessor_MyClass.is_instance_or_derived(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubClass.is_instance_or_derived(my_class))
        self.assertTrue(DataProcessor_MySubClass.is_instance_or_derived(my_sub_class))
        self.assertTrue(DataProcessor_MySubClass.is_instance_or_derived(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubSubClass.is_instance_or_derived(my_class))
        self.assertFalse(DataProcessor_MySubSubClass.is_instance_or_derived(my_sub_class))
        self.assertTrue(DataProcessor_MySubSubClass.is_instance_or_derived(my_sub_sub_class))

        config = BuilderConfig()
        # Caution: when adding to the custom processor list and relying on inheritance,
        #   the child/leaf classes should be first and the base classes at the end.
        config.custom_pre_processors.extend(
            [DataProcessor_MySubSubClass(), DataProcessor_MySubClass(), DataProcessor_MyClass()]
        )
        config.attr_flags = AttributeFlags.INC_ALL_DEBUG
        builder = Builder(config)

        e: ET.Element = builder.build([my_class, my_sub_class, my_sub_sub_class])
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if test_cases_config_rewrite_expected_output:
            with open(
                './tests/expected_test_custom_data_processors_using_inheritance.INC_ALL_DEBUG.xml',
                'w',
                encoding="utf-8"
            ) as f:
                f.write(result)

        with open(
            './tests/expected_test_custom_data_processors_using_inheritance.INC_ALL_DEBUG.xml',
            'r',
            encoding="utf-8"
        ) as f:
            expected = f.read()

        self.assertEqual(result, expected)

    def test_custom_data_processors_without_inheritance(self):
        class DataProcessor_MyClass(DataProcessorBaseClass):
            # @ final
            @ staticmethod
            def is_MyClass(data: Any) -> bool:
                return isinstance(data, MyClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MyClass.is_MyClass(data):
                    return None
                new_tag: str = data.__class__.__name__
                current = config.SubElement(parent, new_tag)
                config.process(parent=current, data=data.name, child_name='name')
                return current

        class DataProcessor_MySubClass(DataProcessorBaseClass):
            # @ final
            @ staticmethod
            def is_MySubClass(data: Any) -> bool:
                return isinstance(data, MySubClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MySubClass.is_MySubClass(data):
                    return None
                new_tag: str = data.__class__.__name__
                current = config.SubElement(parent, new_tag)
                config.process(parent=current, data=data.name, child_name='name')
                config.process(parent=current, data=data.ip_addr, child_name='ip_addr')
                config.process(parent=current, data=data.port, child_name='port')
                config.process(parent=current, data=data._MySubClass__private_instance_var, child_name='__private_instance_var')
                return current

        class DataProcessor_MySubSubClass(DataProcessorBaseClass):
            # @ final
            @ staticmethod
            def is_MySubSubClass(data: Any) -> bool:
                return isinstance(data, MySubSubClass)

            def create_tree(
                    self,
                    config: CLASS_BUILDER_CONFIG,
                    parent: ET.Element,
                    data: Any,
                    child_name: Optional[str] = None,
                    **kwargs: object
            ) -> DATA_PROCESSOR_RETURN_TYPE:
                if not DataProcessor_MySubSubClass.is_MySubSubClass(data):
                    return None
                new_tag: str = data.__class__.__name__
                current = config.SubElement(parent, new_tag)
                config.process(parent=current, data=data.name, child_name='name')
                config.process(parent=current, data=data.ip_addr, child_name='ip_addr')
                config.process(parent=current, data=data.port, child_name='port')
                config.process(parent=current, data=data._MySubClass__private_instance_var, child_name='__private_instance_var')
                config.process(parent=current, data=data.geolocation, child_name='geolocation')
                config.process(parent=current, data=data.instance_var, child_name='instance_var')
                return current

        # Verify the "is_" functions are recognizing the hierarchy
        my_class = MyClass()
        my_sub_class = MySubClass()
        my_sub_sub_class = MySubSubClass()

        self.assertTrue(DataProcessor_MyClass.is_MyClass(my_class))
        self.assertTrue(DataProcessor_MyClass.is_MyClass(my_sub_class))
        self.assertTrue(DataProcessor_MyClass.is_MyClass(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubClass.is_MySubClass(my_class))
        self.assertTrue(DataProcessor_MySubClass.is_MySubClass(my_sub_class))
        self.assertTrue(DataProcessor_MySubClass.is_MySubClass(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubSubClass.is_MySubSubClass(my_class))
        self.assertFalse(DataProcessor_MySubSubClass.is_MySubSubClass(my_sub_class))
        self.assertTrue(DataProcessor_MySubSubClass.is_MySubSubClass(my_sub_sub_class))

        config = BuilderConfig()
        # Caution: when adding to the custom processor list and relying on inheritance,
        #   the child/leaf classes should be first and the base classes at the end.
        config.custom_pre_processors.extend(
            [DataProcessor_MySubSubClass(), DataProcessor_MySubClass(), DataProcessor_MyClass()]
        )
        config.attr_flags = AttributeFlags.INC_ALL_DEBUG
        builder = Builder(config)

        e: ET.Element = builder.build([my_class, my_sub_class, my_sub_sub_class])
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if test_cases_config_rewrite_expected_output:
            with open(
                './tests/expected_test_custom_data_processors_without_inheritance.INC_ALL_DEBUG.xml',
                'w',
                encoding="utf-8"
            ) as f:
                f.write(result)

        with open(
            './tests/expected_test_custom_data_processors_without_inheritance.INC_ALL_DEBUG.xml',
            'r',
            encoding="utf-8"
        ) as f:
            expected = f.read()

        self.assertEqual(result, expected)

    def test_Builder_init(self):
        b = Builder()
        self.assertIsNotNone(b.config)

    def test_codec_getter_setter(self):
        config = BuilderConfig()
        cwText = CodecWrapper()
        cwText.codec_name = 'utf_8'
        cwBin = CodecWrapper()
        cwBin.codec_name = 'zip'

        config.codec_text = cwText
        self.assertEqual(config.codec_text, cwText)

        config.codec_binary = cwBin
        self.assertEqual(config.codec_binary, cwBin)

    def test_element_constructors(self):
        attr_parent: Final[Dict[str, str]] = {"key_test_parent": "val_test_parent"}
        attr_sub: Final[Dict[str, str]] = {"key_test_sub": "val_test_sub"}
        config = BuilderConfig()
        eParent = config.Element('Test_Parent', attr_parent)
        eSub = config.SubElement(eParent, 'test_sub', attr_sub)
        self.assertEqual(eParent.attrib, attr_parent)
        self.assertEqual(eSub.attrib, attr_sub)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
