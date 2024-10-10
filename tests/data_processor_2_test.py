"""
Additional unit tests
"""
# pylint: disable=C0103,C0114,C0115,C0116,C0301
#   C0103 invalid-name
#   C0114 missing-module-docstring
#   C0115 missing-class-docstring
#   C0116 missing-function-docstring
#   C0301 line-too-long
import xml.etree.ElementTree as ET
import unittest
from typing import Any, Optional, cast, override
from libs.abstract_baseclasses import DataProcessorAbstractBaseClass, XmlElementTypeAlias
from libs.attributes import AttributeFlags
from libs.config import Config
from libs.data_processor import DataProcessor_post_processor_for_classes
from libs.xml_element_wrapper_converters import convert_to_etree
from tests.config_test_cases import TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT
from tests.predefined_test_cases import MyClass, MySubClass, MySubSubClass, TEST_CASE


class TestDataProcessor2(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.config = Config()

    def test_default_test_cases(self):
        # config.attr_flags = AttributeFlags.NONE
        self.config.attr_flags = AttributeFlags.INC_ALL_DEBUG
        ew = DataProcessorAbstractBaseClass.convert_to_xml(
            config=self.config,
            data=TEST_CASE
        )

        e = convert_to_etree(ew)
        assert e is not None
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT:
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
        class DataProcessor_MyClass(DataProcessor_post_processor_for_classes):
            @staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MyClass)

            @override
            def _get_default_element_name(self, data: Any) -> str:
                return data.__class__.__name__

            @override
            def _get_element_name_from_config(self) -> Optional[str]:
                return self.config.override_class_label

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return DataProcessor_MyClass.is_instance_or_derived(data)

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
                    data=cast(MyClass, data).name,
                    child_name='name'
                )

        class DataProcessor_MySubClass(DataProcessor_MyClass):
            # @ final
            @ staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MySubClass)

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return DataProcessor_MySubClass.is_instance_or_derived(data)

            @override
            def _recursively_process_any_nested_objects(
                self,
                parent: XmlElementTypeAlias,
                current: XmlElementTypeAlias,
                data: Any,
                child_name: Optional[str] = None,
                **kwargs: object
            ) -> None:
                super()._recursively_process_any_nested_objects(
                    parent=parent,
                    current=current,
                    data=data,
                    child_name=child_name,
                    kwargs=kwargs
                )
                mysubclass: MySubClass = cast(MySubClass, data)
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.ip_addr,
                    child_name='ip_addr'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.port,
                    child_name='port'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass._MySubClass__private_instance_var,  # pylint: disable=W0212; protected-access # type: ignore
                    child_name='__private_instance_var'
                )

        class DataProcessor_MySubSubClass(DataProcessor_MySubClass):
            # @ final
            @ staticmethod
            def is_instance_or_derived(data: Any) -> bool:
                return isinstance(data, MySubSubClass)

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return DataProcessor_MySubSubClass.is_instance_or_derived(data)

            @override
            def _recursively_process_any_nested_objects(
                self,
                parent: XmlElementTypeAlias,
                current: XmlElementTypeAlias,
                data: Any,
                child_name: Optional[str] = None,
                **kwargs: object
            ) -> None:
                super()._recursively_process_any_nested_objects(
                    parent=parent,
                    current=current,
                    data=data,
                    child_name=child_name,
                    kwargs=kwargs
                )
                mysubsubclass: MySubSubClass = cast(MySubSubClass, data)
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.geolocation,
                    child_name='geolocation'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.instance_var,
                    child_name='instance_var'
                )

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

        self.config = Config()
        # Caution: when adding to the custom processor list and relying on inheritance,
        #   the child/leaf classes should be first and the base classes at the end.
        self.config.custom_pre_processors.extend(
            [
                DataProcessor_MySubSubClass(self.config),
                DataProcessor_MySubClass(self.config),
                DataProcessor_MyClass(self.config)
            ]
        )
        self.config.attr_flags = AttributeFlags.INC_ALL_DEBUG

        ew: XmlElementTypeAlias = DataProcessorAbstractBaseClass.convert_to_xml(
            config=self.config,
            data=[my_class, my_sub_class, my_sub_sub_class]
        )
        e: ET.Element = convert_to_etree(ew)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT:
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
        class DataProcessor_MyClass(DataProcessorAbstractBaseClass):
            @ staticmethod
            def is_MyClass(data: Any) -> bool:
                return isinstance(data, MyClass) and issubclass(MyClass, type(data))

            @override
            def _get_default_element_name(self, data: Any) -> str:
                return 'MyClass'

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return self.is_MyClass(data)

            @override
            def _recursively_process_any_nested_objects(
                self,
                parent: XmlElementTypeAlias,
                current: XmlElementTypeAlias,
                data: Any,
                child_name: Optional[str] = None,
                **kwargs: object
            ) -> None:
                myclass: MyClass = cast(MyClass, data)
                self._process(
                    config=self.config,
                    parent=current,
                    data=myclass.name,
                    child_name='name'
                )

        class DataProcessor_MySubClass(DataProcessorAbstractBaseClass):
            # @ final
            @ staticmethod
            def is_MySubClass(data: Any) -> bool:
                return isinstance(data, MySubClass) and issubclass(MySubClass, type(data))

            @override
            def _get_default_element_name(self, data: Any) -> str:
                return 'MyClass'

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return self.is_MySubClass(data)

            @override
            def _recursively_process_any_nested_objects(
                self,
                parent: XmlElementTypeAlias,
                current: XmlElementTypeAlias,
                data: Any,
                child_name: Optional[str] = None,
                **kwargs: object
            ) -> None:
                mysubclass: MySubClass = cast(MySubClass, data)
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.name,
                    child_name='name'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.dummy,
                    child_name='dummy'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.ip_addr,
                    child_name='ip_addr'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubclass.port,
                    child_name='port'
                )

        class DataProcessor_MySubSubClass(DataProcessorAbstractBaseClass):
            # @ final
            @ staticmethod
            def is_MySubSubClass(data: Any) -> bool:
                return isinstance(data, MySubSubClass) and issubclass(MySubSubClass, type(data))

            @override
            def _get_default_element_name(self, data: Any) -> str:
                return 'MyClass'

            @override
            def _is_expected_data_type(self, data: Any) -> bool:
                return self.is_MySubSubClass(data)

            @override
            def _recursively_process_any_nested_objects(
                self,
                parent: XmlElementTypeAlias,
                current: XmlElementTypeAlias,
                data: Any,
                child_name: Optional[str] = None,
                **kwargs: object
            ) -> None:
                mysubsubclass: MySubSubClass = cast(MySubSubClass, data)
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.name,
                    child_name='name'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.dummy,
                    child_name='dummy'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.ip_addr,
                    child_name='ip_addr'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.port,
                    child_name='port'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.__private_instance_var,   # type: ignore  pylint: disable=W0212; protected-access
                    child_name='__private_instance_var'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.geolocation,
                    child_name='geolocation'
                )
                self._process(
                    config=self.config,
                    parent=current,
                    data=mysubsubclass.instance_var,
                    child_name='instance_var'
                )

        # Verify the "is_" functions are recognizing the hierarchy
        my_class = MyClass()
        my_sub_class = MySubClass()
        my_sub_sub_class = MySubSubClass()

        self.assertTrue(DataProcessor_MyClass.is_MyClass(my_class))
        self.assertFalse(DataProcessor_MyClass.is_MyClass(my_sub_class))
        self.assertFalse(DataProcessor_MyClass.is_MyClass(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubClass.is_MySubClass(my_class))
        self.assertTrue(DataProcessor_MySubClass.is_MySubClass(my_sub_class))
        self.assertFalse(DataProcessor_MySubClass.is_MySubClass(my_sub_sub_class))

        self.assertFalse(DataProcessor_MySubSubClass.is_MySubSubClass(my_class))
        self.assertFalse(DataProcessor_MySubSubClass.is_MySubSubClass(my_sub_class))
        self.assertTrue(DataProcessor_MySubSubClass.is_MySubSubClass(my_sub_sub_class))

        config = Config()
        # Caution: when adding to the custom processor list and relying on inheritance,
        #   the child/leaf classes should be first and the base classes at the end.
        config.custom_pre_processors.extend(
            [
                DataProcessor_MySubSubClass(config),
                DataProcessor_MySubClass(config),
                DataProcessor_MyClass(config)
            ]
        )
        config.attr_flags = AttributeFlags.INC_ALL_DEBUG

        ew: XmlElementTypeAlias = DataProcessorAbstractBaseClass.convert_to_xml(
            config=self.config,
            data=[my_class, my_sub_class, my_sub_sub_class]
        )
        e: ET.Element = convert_to_etree(ew)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT:
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

    # def test_codec_getter_setter(self):
    #     config = BuilderConfig()
    #     cwText = CodecWrapper()
    #     cwText.codec_name = 'utf_8'
    #     cwBin = CodecWrapper()
    #     cwBin.codec_name = 'zip'

    #     config.codec_text = cwText
    #     self.assertEqual(config.codec_text, cwText)

    #     config.codec_binary = cwBin
    #     self.assertEqual(config.codec_binary, cwBin)

    # def test_element_constructors(self):
    #     attr_parent: Final[XmlAttributesTypeAlias] = {"key_test_parent": "val_test_parent"}
    #     attr_sub: Final[XmlAttributesTypeAlias] = {"key_test_sub": "val_test_sub"}
    #     config = BuilderConfig()
    #     eParent = config.Element('Test_Parent', attr_parent)
    #     eSub = config.SubElement(eParent, 'test_sub', attr_sub)
    #     self.assertEqual(eParent.attrib, attr_parent)
    #     self.assertEqual(eSub.attrib, attr_sub)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
