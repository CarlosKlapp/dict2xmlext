import array
import calendar
import sys
from typing import Any, List, Optional, final
import unittest
from uuid import UUID
import xml.etree.ElementTree as ET
from libs.builder import Builder, BuilderConfig
from libs.attributes import AttributeFlags, AttributeFlagsNames
from libs.builder_baseclass import CLASS_BUILDER_CONFIG, DATA_PROCESSOR_RETURN_TYPE
from libs.codec_wrapper import CodecWrapper
from libs.data_processor import DataProcessor_BaseClass, DataProcessor_binary, DataProcessor_post_processor_for_classes, DataProcessor_tzinfo, DataProcessor_used_for_testing, DataProcessor_used_for_testing_use_hints
import datetime as dt
from dateutil import tz
from collections import namedtuple
from zoneinfo import ZoneInfo
from tests.config_test_cases import test_cases_config_rewrite_expected_output
from tests.predefined_test_cases import list_of_my_classes


Point3D = namedtuple('Point', ['x', 'y', 'z'])


class TestDataProcessor(unittest.TestCase):
    test_data = [
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

    @ staticmethod
    def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
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

    def baseclass_test_helper(self, dp: DataProcessor_BaseClass):
        config = BuilderConfig()
        et = config.Element(tag=config.root_label)

        self.assertIsNone(dp.get_field_type_hint('dummy'))
        self.assertIsNone(dp.get_format_string_hint('dummy'))

        d = dp.attr_alt_id(config, et, et, 'dummy')
        self.assertListEqual(list(d.keys()), [AttributeFlagsNames[AttributeFlags.INC_ALT_ID]])
        self.assertTrue(self.is_valid_uuid(list(d.values())[0]))

        d = dp.attr_binary_encoding(config, et, et, 'dummy')
        self.assertListEqual(list(d.keys()), [AttributeFlagsNames[AttributeFlags.INC_BINARY_ENCODING]])
        self.assertTrue(list(d.values())[0] == 'base64')

        d = dp.attr_field_type_hint(config, et, et, 'dummy')
        self.assertDictEqual(d, {})

        d = dp.attr_format_string_hint(config, et, et, 'dummy')
        self.assertDictEqual(d, {})

        d = dp.attr_len(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_LEN]: str(len('dummy'))})

        d = dp.attr_python_data_type(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_PYTHON_DATA_TYPE]: str(type('dummy'))[1:-1]})

        d = dp.attr_size_bytes(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_SIZE_BYTES]: str(sys.getsizeof('dummy'))})

        d = dp.attr_xsd_data_type(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_XSD_DATA_TYPE]: 'anyType'})

    def test_add_attributes(self):
        config = BuilderConfig()
        etParent = config.Element(tag=config.root_label)
        et = ET.SubElement(etParent, 'test')
        dp = DataProcessor_used_for_testing()

    def test_is_bool(self):
        func = DataProcessor_BaseClass.is_bool
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_binary(self):
        func = DataProcessor_BaseClass.is_binary
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_bytearray(self):
        func = DataProcessor_BaseClass.is_bytearray
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_bytes(self):
        func = DataProcessor_BaseClass.is_bytes
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_calendar(self):
        func = DataProcessor_BaseClass.is_calendar
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False]
        self.assertListEqual(resp, expected)

    def test_is_date(self):
        func = DataProcessor_BaseClass.is_date
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_datetime(self):
        func = DataProcessor_BaseClass.is_datetime
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False]
        self.assertListEqual(resp, expected)

    def test_is_dict(self):
        func = DataProcessor_BaseClass.is_dict
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_enum(self):
        func = DataProcessor_BaseClass.is_enum
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_namedtuple(self):
        func = DataProcessor_BaseClass.is_namedtuple
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]
        self.assertListEqual(resp, expected)

    def test_is_none(self):
        func = DataProcessor_BaseClass.is_none
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_numeric(self):
        func = DataProcessor_BaseClass.is_numeric
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_sequence(self):
        func = DataProcessor_BaseClass.is_sequence
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_str(self):
        func = DataProcessor_BaseClass.is_str
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_time(self):
        func = DataProcessor_BaseClass.is_time
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_timedelta(self):
        func = DataProcessor_BaseClass.is_timedelta
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_timezone(self):
        func = DataProcessor_BaseClass.is_timezone
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_is_tzinfo(self):
        func = DataProcessor_BaseClass.is_tzinfo
        resp = [func(x[0]) for x in self.test_data]
        dbg = [(x[1], func(x[0]), x[2]) for x in self.test_data]
        expected = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False]
        self.assertListEqual(resp, expected)

    def test_DataProcessor_BaseClass(self):
        dp = DataProcessor_used_for_testing()
        self.baseclass_test_helper(dp)

        config = BuilderConfig()
        etParent = config.Element(tag=config.root_label)
        self.assertIsNone(dp.process(config, etParent, 'dummy'))

    def test_DataProcessor_with_hints(self):
        dp = DataProcessor_used_for_testing_use_hints()
        self.assertEqual(dp.get_field_type_hint('dummy'), 'test- get_field_type_hint')
        self.assertEqual(dp.get_format_string_hint('dummy'), 'test- get_format_string_hint')

        config = BuilderConfig()
        et = config.Element(tag=config.root_label)

        d = dp.attr_field_type_hint(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_FIELD_TYPE_HINT]: 'test- get_field_type_hint'})

        d = dp.attr_format_string_hint(config, et, et, 'dummy')
        self.assertDictEqual(d, {AttributeFlagsNames[AttributeFlags.INC_FORMAT_STRING_HINT]: 'test- get_format_string_hint'})

    def test_DataProcessor_tzinfo(self):
        dp = DataProcessor_tzinfo()
        config = BuilderConfig()
        builder = Builder(config)

        e = builder.build(data=tz.gettz('America/Chicago'))
        assert e is not None
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, '<root>\n  <tzinfo>America/Chicago</tzinfo>\n</root>')

        e = builder.build(data=tz.gettz())
        assert e is not None
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, '<root>\n  <tzinfo>/etc/localtime</tzinfo>\n</root>')

    def test_DataProcessor_binary_encoder(self):
        dp = DataProcessor_binary()
        self.baseclass_test_helper(dp)

        config = BuilderConfig()
        cw = CodecWrapper()
        cw.codec_name = 'zip'
        config.codec_binary = cw
        etParent = config.Element(tag=config.root_label)
        e = dp.process(config, etParent, b'dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy-dummy')
        self.assertIsNotNone(e)
        assert e is not None
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')
        self.assertEqual(result, '<binary>789c4b29cdcdadd44d219f04004d5e19a7</binary>')

    def test_DataProcessor_class_custom_post_processor(self):
        # cspell:ignore unmangled
        dp = DataProcessor_post_processor_for_classes()
        config = BuilderConfig()

        config.attr_flags = AttributeFlags.NONE
        builder = Builder(config)

        e = builder.build(data=list_of_my_classes)
        assert e is not None
        ET.indent(e)
        result = ET.tostring(e, encoding='unicode')

        if test_cases_config_rewrite_expected_output:
            with open('./tests/expected_test_DataProcessor_class_custom_post_processor.mangled.xml', 'w', encoding="utf-8") as f:
                f.write(result)

        with open('./tests/expected_test_DataProcessor_class_custom_post_processor.mangled.xml', 'r', encoding="utf-8") as f:
            expected = f.read()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
