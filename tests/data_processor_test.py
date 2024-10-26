# flake8: noqa: F841
#   F841 - unused variables
# pyright: reportUnusedVariable=false, reportPrivateUsage=false
# pylint: disable=W0612,W0613,C0103,C0115,C0116,C0301,W0212
#   W0612 - unused variables
#   W0613 - unused-argument
#   C0103 - invalid-name
#   C0115,C0116 - missing docstring
#   C0301 - line too long
#   W0212 - protected-access
"""
Unit tests for data processing code
"""
from typing import Any, List, NamedTuple
from zoneinfo import ZoneInfo
from uuid import UUID
import array
import xml.etree.ElementTree as ET
import datetime as dt
import calendar
import unittest
import tzlocal
from dateutil import tz
from libs.abstract_baseclasses import XmlAttributesTypeAlias, XmlElementBaseClass
from libs.attributes import AttributeFlags, ATTRIBUTE_FLAGS_NAMES
from libs.codec_wrapper import CodecWrapper
from libs.config import Config
from libs.data_processor import (
    DataProcessorAbstractBaseClass,
    DataProcessor_binary,
    DataProcessor_tzinfo,
    DataProcessor_used_for_testing,
    DataProcessor_used_for_testing_use_hints
)
from libs.data_type_identification import DataTypeIdentification
from libs.misc import islinux
from libs.xml_element_wrapper_converters import convert_to_etree
from tests.config_test_cases import TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT
from tests.predefined_test_cases import TEST_CASE, list_of_my_classes


class Point3D(NamedTuple):
    x: int
    y: int
    z: int


class TestDataProcessor(unittest.TestCase):
    test_data: List[Any] = [
        (None, str(type(None)), 'none'),
        (True, str(type(True)), 'bool: True'),
        (False, str(type(False)), 'bool: False'),
        (AttributeFlags.INC_ALL, str(type(AttributeFlags.INC_ALL)), 'Enum'),
        ('dummy', str(type('dummy')), 'string'),
        (435, str(type(435)), 'int'),
        (7.87, str(type(7.87)), 'float'),
        ('dummy'.encode('utf-8'), str(type('dummy'.encode('utf-8'))), 'bytes'),
        (bytearray(1234678), str(type(bytearray(5))), 'bytearray'),
        ([323], str(type([323])), 'list'),
        ((12345, 54321, 'hello!'), str(type((12345, 54321, 'hello!'))), 'tuple'),
        ({453}, str(type({453})), 'set'),
        (range(10), str(type(range(10))), 'range'),
        (array.array('i', [1, 2, 3]), str(type(array.array('i', [1, 2, 3]))), 'array'),
        ({'foo': 'bar'}, str(type({'foo': 'bar'})), 'dict'),
        (dt.timedelta(days=50), str(type(dt.timedelta(days=50))), 'timedelta'),
        (tz.gettz('America/Chicago'), str(type(tz.gettz('America/Chicago'))), 'tzinfo'),  # cSpell:ignore gettz
        (ZoneInfo('America/Chicago'), str(type(ZoneInfo('America/Chicago'))), 'ZoneInfo'),
        (dt.timezone(dt.timedelta(hours=-9), 'test'), str(type(dt.timezone(dt.timedelta(hours=-9), 'test'))), 'timezone'),
        (dt.time(), str(type(dt.time())), 'time'),
        (dt.date.today(), str(type(dt.date.today())), 'date'),
        (dt.datetime.now(), str(type(dt.datetime.now())), 'datetime'),
        (calendar.Calendar(), str(type(calendar.Calendar())), 'calendar'),
        (Point3D(x=11, y=13, z=17), str(type(Point3D(x=11, y=13, z=17))), 'named-tuple'),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.datatypeidentification = DataTypeIdentification()
        self.config = Config()

    @ staticmethod
    def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
        """
        Check if uuid_to_test is a valid UUID.

        Parameters
        ----------
        uuid_to_test : str
        version : {1, 2, 3, 4}

        Returns
        -------
        `True` if uuid_to_test is a valid UUID, otherwise `False`.

        Examples
        --------
        >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
        True
        >>> is_valid_uuid('c9bf9e58')
        False
        """

        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    def test_is_valid_uuid(self):
        self.assertTrue(self.is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a'))
        self.assertFalse(self.is_valid_uuid('foobar'))
        self.assertFalse(self.is_valid_uuid(''))

    def baseclass_test_helper(self, dp: DataProcessorAbstractBaseClass):
        et_parent = XmlElementBaseClass.create_root_element(config=self.config)
        et_current = et_parent.create_child_element(config=self.config, tag='dummy', text='dummy')
        assert et_current.text is not None

        self.assertIsNone(dp._get_field_type_hint('dummy'))
        self.assertIsNone(dp._get_format_string_hint('dummy'))

        d: XmlAttributesTypeAlias = dp._attr_alt_id(et_parent, et_current, 'dummy')
        self.assertListEqual(list(d.keys()), [ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_ALT_ID]])
        self.assertTrue(self.is_valid_uuid(list(d.values())[0]))

        d = dp._attr_binary_encoding(et_parent, et_current, 'dummy')
        self.assertListEqual(list(d.keys()), [ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_BINARY_ENCODING]])
        self.assertTrue(list(d.values())[0] == 'base64')

        d = dp._attr_field_type_hint(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {})

        d = dp._attr_format_string_hint(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {})

        d = dp._attr_len(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_LEN]: str(len('dummy'))})

        d = dp._attr_python_data_type(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_PYTHON_DATA_TYPE]: str(type('dummy'))[1:-1]})

        d = dp._attr_length_element_text(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_LENGTH_ELEMENT_TEXT]: str(len(et_current.text))})

        d = dp._attr_xsd_data_type(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_XSD_DATA_TYPE]: 'anyType'})

    def test_add_attributes(self):
        et_parent = XmlElementBaseClass.create_root_element(config=self.config)
        et_current = et_parent.create_child_element(config=self.config, tag='test')

        dp = DataProcessor_used_for_testing(self.config)

    def test_is_bool(self):
        func = self.datatypeidentification.is_bool
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_binary(self):
        func = self.datatypeidentification.is_binary
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_bytearray(self):
        func = self.datatypeidentification.is_bytearray
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_bytes(self):
        func = self.datatypeidentification.is_bytes
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_calendar(self):
        func = self.datatypeidentification.is_calendar
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False]
        self.assertListEqual(resp, expected)

    def test_is_date(self):
        func = self.datatypeidentification.is_date
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_datetime(self):
        func = self.datatypeidentification.is_datetime
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False]
        self.assertListEqual(resp, expected)

    def test_is_dict(self):
        func = self.datatypeidentification.is_dict
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_enum(self):
        func = self.datatypeidentification.is_enum
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_namedtuple(self):
        func = self.datatypeidentification.is_namedtuple
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]
        self.assertListEqual(resp, expected)

    def test_is_none(self):
        func = self.datatypeidentification.is_none
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_numeric(self):
        func = self.datatypeidentification.is_numeric
        resp = [func(x[0]) for x in self.test_data]
        expected = [False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_sequence(self):
        func = self.datatypeidentification.is_sequence
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_str(self):
        func = self.datatypeidentification.is_str
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_time(self):
        func = self.datatypeidentification.is_time
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_timedelta(self):
        func = self.datatypeidentification.is_timedelta
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_timezone(self):
        func = self.datatypeidentification.is_timezone
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_tzinfo(self):
        func = self.datatypeidentification.is_tzinfo
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_DataProcessor_BaseClass(self):
        dp = DataProcessor_used_for_testing(self.config)
        self.baseclass_test_helper(dp)

        et_parent = XmlElementBaseClass.create_root_element(config=self.config)
        self.assertIsNotNone(dp.convert_to_xml(self.config, 'dummy'))

    def test_DataProcessor_with_hints(self):
        dp = DataProcessor_used_for_testing_use_hints(self.config)
        self.assertEqual(dp._get_field_type_hint('dummy'), 'test- get_field_type_hint')
        self.assertEqual(dp._get_format_string_hint('dummy'), 'test- get_format_string_hint')

        et_parent = XmlElementBaseClass.create_root_element(config=self.config)
        et_current = et_parent.create_child_element(config=self.config, tag='dummy')

        d = dp._attr_field_type_hint(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_FIELD_TYPE_HINT]: 'test- get_field_type_hint'})

        d = dp._attr_format_string_hint(et_parent, et_current, 'dummy')
        self.assertDictEqual(d, {ATTRIBUTE_FLAGS_NAMES[AttributeFlags.INC_FORMAT_STRING_HINT]: 'test- get_format_string_hint'})

    def test_DataProcessor_tzinfo(self):
        dp = DataProcessor_tzinfo(self.config)

        ew = dp.convert(parent=None, data=tz.gettz('America/Chicago'))
        assert ew is not None
        e = convert_to_etree(ew)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, '<root>\n  <tzinfo>America/Chicago</tzinfo>\n</root>')

        ew = dp.convert(parent=None, data=tz.gettz())
        assert ew is not None
        e = convert_to_etree(ew)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, f'<root>\n  <tzinfo>{tzlocal.get_localzone_name()}</tzinfo>\n</root>')

    def test_DataProcessor_binary_encoder(self):
        dp = DataProcessor_binary(self.config)
        self.baseclass_test_helper(dp)

        cw = CodecWrapper()
        cw.codec_name = 'zip'
        self.config.codec_binary = cw
        et_parent = XmlElementBaseClass.create_root_element(config=self.config)
        ew = dp.convert(et_parent, b'dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy')
        assert ew is not None
        e = convert_to_etree(ew)
        self.assertIsNotNone(e)
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, '<root>\n  <binary>789c4b29cdcdadd44d219f04004d5e19a7</binary>\n</root>')

    def test_DataProcessor_class_custom_post_processor(self):
        # cspell:ignore unmangled
        self.config.attr_flags = AttributeFlags.NONE

        ew = DataProcessorAbstractBaseClass.convert_to_xml(
            config=self.config,
            data=list_of_my_classes
        )
        assert ew is not None
        e = convert_to_etree(ew)
        result = ET.tostring(e, encoding='unicode')

        if TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT:
            with open('./tests/expected_test_DataProcessor_class_custom_post_processor.mangled.xml', 'w', encoding="utf-8") as f:
                f.write(result)

        with open('./tests/expected_test_DataProcessor_class_custom_post_processor.mangled.xml', 'r', encoding="utf-8") as f:
            expected = f.read()
        self.assertEqual(result, expected)

    def test_DataProcessor_class_custom_post_processor_2(self):
        # cspell:ignore unmangled
        self.config.attr_flags = AttributeFlags.INC_ALL_DEBUG

        ew = DataProcessorAbstractBaseClass.convert_to_xml(
            config=self.config,
            data=TEST_CASE
        )
        assert ew is not None
        e = convert_to_etree(ew)
        result = ET.tostring(e, encoding='unicode')

        filename: str
        if islinux():
            filename = './tests/expected_test_DataProcessor_class_custom_post_processor_2_linux.xml'
        else:
            filename = './tests/expected_test_DataProcessor_class_custom_post_processor_2_windows.xml'

        if TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT:
            with open(filename, 'w', encoding="utf-8") as f:
                f.write(result)

        with open(filename, 'r', encoding="utf-8") as f:
            expected = f.read()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
