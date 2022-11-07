import enum
from typing import Dict


class AttributeFlags(enum.Flag):
    NONE = 0
    INC_ALT_ID = enum.auto()
    INC_BINARY_ENCODING = enum.auto()
    INC_DEBUG_INFO = enum.auto()  # not included by default
    INC_FIELD_COMMENT = enum.auto()
    INC_FIELD_TYPE_HINT = enum.auto()
    INC_FORMAT_STRING_HINT = enum.auto()
    INC_LEN = enum.auto()
    INC_PYTHON_DATA_TYPE = enum.auto()
    INC_SEQ_ID = enum.auto()
    INC_SIZE_BYTES = enum.auto()
    INC_XSD_DATA_TYPE = enum.auto()  # not implemented
    INC_ALL = INC_BINARY_ENCODING | INC_FIELD_COMMENT | INC_FIELD_TYPE_HINT | INC_FORMAT_STRING_HINT | INC_LEN | \
        INC_PYTHON_DATA_TYPE | INC_SEQ_ID | INC_SIZE_BYTES | INC_XSD_DATA_TYPE
    INC_ALL_DEBUG = INC_ALL | INC_DEBUG_INFO


AttributeFlagsNames: Dict[AttributeFlags, str] = {
    AttributeFlags.INC_ALT_ID: "alt_id",
    AttributeFlags.INC_BINARY_ENCODING: "binary_encoding",
    AttributeFlags.INC_DEBUG_INFO: "debug_info",
    AttributeFlags.INC_FIELD_COMMENT: "comment",
    AttributeFlags.INC_FIELD_TYPE_HINT: "type_hint",
    AttributeFlags.INC_FORMAT_STRING_HINT: "format_string_hint",
    AttributeFlags.INC_LEN: "length",
    AttributeFlags.INC_PYTHON_DATA_TYPE: "py_type",
    AttributeFlags.INC_SEQ_ID: "id",
    AttributeFlags.INC_SIZE_BYTES: "size_bytes",
    AttributeFlags.INC_XSD_DATA_TYPE: "xsd_type",
}
