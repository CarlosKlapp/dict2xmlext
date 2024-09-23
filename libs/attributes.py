"""
Flags for XML encoding.
"""

import enum
from typing import Dict, Final


class AttributeFlags(enum.Flag):
    """
    Enumeration of the flags that can be set in
    the configuration.
    """

    NONE = 0
    """
    Empty flag - value of Zero
    """

    INC_ALT_ID = enum.auto()
    """
    Assigns a UUID identifier for each XML element. Adds an `alt_id` attribute
    to each element. `<element alt_id="3f5017be-a314-4bb2-92c0-5135b47f8c45">`.

    The UUID value will change each time the code is executed.
    """

    INC_BINARY_ENCODING = enum.auto()
    """
    Indicates the type of encoding used to represent binary data. The name of
    the codec is added as an attribute in the element.

    `<element binary_encoding="base64">ZHVtbXk=</bytes>`
    """

    INC_DEBUG_INFO = enum.auto()  # not included by default
    """
    Not included by default.

    Include debug information as an attribute in the element. The default
    implementation adds the name of the DataProcessor used to encode
    the data.

    `<element debug_info="processed_by:DataProcessor_bool">`
    """

    INC_FIELD_COMMENT = enum.auto()
    """
    Includes comments from the DataProcessor to assist in understanding
    how the data is enocded or what it represents.

    `<element comment="IANA time zone database key
    (e.g. America/New_York, Europe/Paris or Asia/Tokyo)">
    America/Chicago</element>`
    """

    INC_FIELD_TYPE_HINT = enum.auto()
    """
    Adds a hint in the XML attributes as to the type of data that was encoded
    to text.

    For example, `<element_name type_hint="namedtuple">...</element_name>`
    """

    INC_FORMAT_STRING_HINT = enum.auto()
    """
    Includes formatting hints from the DataProcessor to assist in understanding
    how the data is enocded or what it represents.

    `<element format_string_hint="YYYY-MM-DDTHH:MM:SS.ffffff">2022-11-12T14:12:05.000078</element>`
    """

    INC_LEN = enum.auto()
    """
    Will include the number of items in the container object or string. For example,
    in the following list ['a', 'bc', 'def']

    `<list length="3">
        <str length="1">a</str>
        <str length="2">bc</str>
        <str length="3">def</str>
    </l1>`
    """

    INC_PYTHON_DATA_TYPE = enum.auto()
    """
    Includes the Python data type containing the data.

    `<element py_type="class 'str'">text</element>`
    """

    INC_SEQ_ID = enum.auto()
    """
    Uses a sequential counter for each XML element. Adds an `id` attribute
    to each element. `<element id="1">`.
    """

    INC_LENGTH_ELEMENT_TEXT = enum.auto()
    """
    Adds an XML attribute with the length of the text within the XML element.

    `<element length_element_text="4">text</element>`
    `<element length_element_text="0"></element>`
    """

    INC_XSD_DATA_TYPE = enum.auto()  # not implemented
    """
    Adds an XML attribute with the XSD data type.

    `<element xsd_type="anyType">text</element>`
    """

    INC_ALL = (
        INC_ALT_ID |
        INC_BINARY_ENCODING |
        INC_FIELD_COMMENT |
        INC_FIELD_TYPE_HINT |
        INC_FORMAT_STRING_HINT |
        INC_LEN |
        INC_PYTHON_DATA_TYPE |
        INC_SEQ_ID |
        INC_LENGTH_ELEMENT_TEXT |
        INC_XSD_DATA_TYPE
    )

    INC_ALL_DEBUG = INC_ALL | INC_DEBUG_INFO


ATTRIBUTE_FLAGS_NAMES: Final[Dict[AttributeFlags, str]] = {
    AttributeFlags.INC_ALT_ID: "alt_id",
    AttributeFlags.INC_BINARY_ENCODING: "binary_encoding",
    AttributeFlags.INC_DEBUG_INFO: "debug_info",
    AttributeFlags.INC_FIELD_COMMENT: "comment",
    AttributeFlags.INC_FIELD_TYPE_HINT: "type_hint",
    AttributeFlags.INC_FORMAT_STRING_HINT: "format_string_hint",
    AttributeFlags.INC_LEN: "length",
    AttributeFlags.INC_PYTHON_DATA_TYPE: "py_type",
    AttributeFlags.INC_SEQ_ID: "id",
    AttributeFlags.INC_LENGTH_ELEMENT_TEXT: "length_element_text",
    AttributeFlags.INC_XSD_DATA_TYPE: "xsd_type",
}
